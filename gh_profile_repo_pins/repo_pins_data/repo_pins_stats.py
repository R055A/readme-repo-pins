from gh_profile_repo_pins.repo_pins_exceptions import RepoPinStatsError
from subprocess import run, PIPE, CompletedProcess, CalledProcessError
from concurrent.futures import ThreadPoolExecutor, as_completed
import gh_profile_repo_pins.repo_pins_enum as enums
from tempfile import mkdtemp
from shutil import rmtree
from os import environ


class RepoPinStats:

    __TMP_DIR: str = "tmp_git"
    __IS_CALLED_PROCESS_ERR: bool = True
    __MAX_WORKERS: int = 8

    def __init__(self, gh_token: str = None) -> None:
        self.__gh_token: str = gh_token
        self.__completed_git_commit_data_process: CompletedProcess[str] | None = None

    def __get_completed_process(self, args: list[str]) -> CompletedProcess[str]:
        env = environ.copy()
        env.setdefault("GIT_TERMINAL_PROMPT", "0")
        env.setdefault("GIT_OPTIONAL_LOCKS", "0")
        env.setdefault("GIT_ASKPASS", "true")
        env.setdefault("GIT_PAGER", "cat")
        return run(
            args=args,
            check=self.__IS_CALLED_PROCESS_ERR,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            env=env,
        )

    def __get_ref(self, tmp_dir: str) -> str | None:
        for _ in range(2):
            try:
                ref: str = self.__get_completed_process(
                    args=[
                        "git",
                        "-C",
                        tmp_dir,
                        "symbolic-ref",
                        "--quiet",
                        "--short",
                        "refs/remotes/origin/HEAD",
                    ]
                ).stdout
                if ref:
                    return ref.strip()

                self.__get_completed_process(
                    args=["git", "-C", tmp_dir, "remote", "set-head", "origin", "-a"]
                )
            except CalledProcessError:
                continue

        try:
            for line in self.__get_completed_process(
                args=["git", "-C", tmp_dir, "ls-remote", "--symref", "origin", "HEAD"]
            ).stdout.splitlines():
                if line.startswith("ref: ") and "\tHEAD" in line:
                    branch = line.split()[1].split("/")[-1]
                    return f"origin/{branch}"
        except CalledProcessError:
            pass

        for default_branch in ["main", "master"]:
            try:
                self.__get_completed_process(
                    args=[
                        "git",
                        "-C",
                        tmp_dir,
                        "show-ref",
                        "--verify",
                        f"refs/remotes/origin/{default_branch}",
                    ]
                )
                return f"origin/{default_branch}"
            except CalledProcessError:
                continue
        return None

    def __fetch_git_commit_data(
        self, url: str, tmp_dir: str
    ) -> CompletedProcess[str] | None:
        self.__get_completed_process(
            args=[
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                url,
                tmp_dir,
            ]
        )
        self.__get_completed_process(
            args=[
                "git",
                "-C",
                tmp_dir,
                "fetch",
                "origin",
                "+refs/heads/*:refs/remotes/origin/*",
                "--filter=blob:none",
            ]
        )

        ref: str = self.__get_ref(tmp_dir=tmp_dir)
        if not ref:
            return None
        try:
            self.__get_completed_process(
                args=["git", "-C", tmp_dir, "rev-list", "-n", "1", ref]
            )
        except CalledProcessError:
            return None

        return self.__get_completed_process(
            args=[
                "git",
                "-C",
                tmp_dir,
                "-c",
                "i18n.logOutputEncoding=UTF-8",
                "log",
                ref,
                "--use-mailmap",
                "--no-merges",
                "--numstat",
                "--format=%aN <%aE>",
            ]
        )

    def __fetch_repo_stats(
        self, owner_repo: str
    ) -> list[dict[str, str | dict[str, int]]]:
        url: str = (
            f"https://{(self.__gh_token + "@") if self.__gh_token else ""}github.com/{owner_repo}.git"
        )
        tmp_dir: str = mkdtemp(prefix=self.__TMP_DIR)

        repo_changes_add, repo_changes_del = {}, {}
        try:
            commit_data: CompletedProcess[str] | None = self.__fetch_git_commit_data(
                url=url, tmp_dir=tmp_dir
            )
            if not commit_data or not commit_data.stdout:
                return []
            cur_commit_author: str | None = None
            for commit_line in commit_data.stdout.splitlines():
                if commit_line.endswith(">") and " <" in commit_line:
                    cur_commit_author = commit_line
                    continue

                commit_line_tokens: list[str] = commit_line.split(sep="\t")
                if len(commit_line_tokens) == 3 and cur_commit_author:
                    a, d, _ = commit_line_tokens
                    if a.isdigit() and d.isdigit():
                        repo_changes_add[cur_commit_author] = repo_changes_add.get(
                            cur_commit_author, 0
                        ) + int(a)
                        repo_changes_del[cur_commit_author] = repo_changes_del.get(
                            cur_commit_author, 0
                        ) + int(d)
        except CalledProcessError as err:
            raise RepoPinStatsError(
                msg=f"Git process error: {err.stderr.strip() or err.stdout.strip() or err}"
            )
        finally:
            rmtree(path=tmp_dir, ignore_errors=True)

        commit_authors: set[str] = set(repo_changes_add) | set(repo_changes_del)
        return [
            {
                enums.RepoPinsResDictKeys.LOGIN.value: commit_author.split(" <")[0]
                .strip()
                .lower(),
                enums.RepoPinsResDictKeys.STATS.value: (
                    repo_changes_add.get(commit_author, 0)
                    + repo_changes_del.get(commit_author, 0)
                ),
            }
            for commit_author in commit_authors
        ]

    def fetch_contribution_stats(self, repo_list: list[dict]) -> list[dict]:
        tasks: list[tuple[str, dict]] = []
        for repo in repo_list:
            if (
                not len(
                    repo.get(enums.RepoPinsResDictKeys.URL.value, "").strip().split("/")
                )
                > 1
                or not repo.get(enums.RepoPinsResDictKeys.NAME.value, "").strip()
            ):
                continue
            tasks.append(
                (
                    f"{repo.get(enums.RepoPinsResDictKeys.URL.value, "").strip().split("/")[-2].strip()}/"
                    f"{repo.get(enums.RepoPinsResDictKeys.NAME.value, "").strip()}",
                    repo,
                )
            )
        with ThreadPoolExecutor(
            max_workers=min(self.__MAX_WORKERS, max(1, len(repo_list)))
        ) as thread_pool:
            contribution_data = {
                thread_pool.submit(self.__fetch_repo_stats, owner_repo): repo
                for owner_repo, repo in tasks
            }
            for k_complete in as_completed(contribution_data):
                contribution_data[k_complete][
                    enums.RepoPinsResDictKeys.CONTRIBUTION.value
                ] = k_complete.result()
        return repo_list
