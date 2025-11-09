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
        self.__url: str | None = None
        self.__tmp_dir: str | None = None
        self.__completed_git_commit_data_process: CompletedProcess[str] | None = None

    def __get_completed_process(self, args: list[str]) -> CompletedProcess[str]:
        env = environ.copy()
        env.setdefault("GIT_TERMINAL_PROMPT", "0")
        env.setdefault("GIT_ASKPASS", "true")
        return run(
            args=args,
            check=self.__IS_CALLED_PROCESS_ERR,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )

    def __fetch_git_commit_data(self) -> None:
        self.__get_completed_process(
            args=[
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                self.__url,
                self.__tmp_dir,
            ]
        )
        self.__get_completed_process(
            args=["git", "-C", self.__tmp_dir, "checkout", "--detach", "origin/HEAD"]
        )
        self.__completed_git_commit_data_process = self.__get_completed_process(
            args=[
                "git",
                "-C",
                self.__tmp_dir,
                "log",
                "--use-mailmap",
                "--no-merges",
                "--numstat",
                "--format=%aN <%aE>",
            ]
        )

    def __fetch_repo_stats(
        self, owner_repo: str
    ) -> list[dict[str, str | dict[str, int]]]:
        self.__url: str = (
            f"https://{(self.__gh_token + "@") if self.__gh_token else ""}github.com/{owner_repo}.git"
        )
        self.__tmp_dir: str = mkdtemp(prefix=self.__TMP_DIR)

        repo_changes_add, repo_changes_del = {}, {}
        try:
            self.__fetch_git_commit_data()
            cur_commit_author: str | None = None
            for (
                commit_line
            ) in self.__completed_git_commit_data_process.stdout.splitlines():
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
            raise RepoPinStatsError(msg=f"Git process error: {str(err)}")
        finally:
            rmtree(path=self.__tmp_dir, ignore_errors=True)

        commit_authors: set[str] = set(repo_changes_add) | set(repo_changes_del)
        return [
            {
                enums.RepoPinsStatsContributionData.LOGIN.value: commit_author,
                enums.RepoPinsStatsContributionData.STATS.value: (
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
                not len(repo.get("url", "").strip().split("/")) > 1
                or not repo.get("name", "").strip()
            ):
                continue
            tasks.append(
                (
                    f"{repo.get("url", "").strip().split("/")[-2].strip()}/{repo.get("name", "").strip()}",
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
                    enums.RepoPinsStatsContributionData.DATA.value
                ] = k_complete.result()
        return repo_list
