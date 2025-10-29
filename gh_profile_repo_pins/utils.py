from logging import basicConfig, getLogger, Logger, StreamHandler, WARNING
from os import environ, getenv, path, listdir, unlink
import gh_profile_repo_pins.repo_pins_enum as enums
from json import load, loads, JSONDecodeError
from argparse import ArgumentParser
from re import sub, DOTALL
from shutil import rmtree
from pathlib import Path
from sys import stdout
from re import compile

USERNAME: str = environ.get("GH_USERNAME", "")
GH_API_TOKEN: str = environ.get("GH_API_TOKEN", "")

# optional, can be a string (for all repos), or a dict (for individual repos)
THEME: str = environ.get("THEME", "")

# optional, an exclusive list of repos (owner/repo separated by commas) with high priority over other optional configs
REPO_NAMES_EXCLUSIVE: str = environ.get("REPO_NAMES_EXCLUSIVE", "")

# optional configs, overrule REPO_NAMES_EXCLUSIVE if not null, otherwise overruled by REPO_NAMES_EXCLUSIVE (default)
NUM_REPO_PINS: str = environ.get("NUM_REPO_PINS", "")
REPO_PIN_ORDER: str = environ.get("REPO_PIN_ORDER", "")

# optional configs, overruled by REPO_NAMES_EXCLUSIVE
IS_EXCLUDE_REPOS_OWNED: str = environ.get("IS_EXCLUDE_REPOS_OWNED", "")
IS_EXCLUDE_REPOS_CONTRIBUTED: str = environ.get("IS_EXCLUDE_REPOS_CONTRIBUTED", "")


def parse_args() -> tuple[str, str, str, str | dict, int, str, bool, bool]:
    parser = ArgumentParser(
        description="GitHub API-fetch pinned/popular repositories for a given username"
    )
    parser.add_argument(
        "--token", type=str, default=GH_API_TOKEN, help="A GitHub API token."
    )
    parser.add_argument(
        "--username",
        type=str,
        default=USERNAME if USERNAME else None,
        help="A GitHub account username.",
    )
    parser.add_argument(
        "--repos",
        type=str,
        default=(
            REPO_NAMES_EXCLUSIVE
            if REPO_NAMES_EXCLUSIVE and len(REPO_NAMES_EXCLUSIVE) > 0
            else None
        ),
        help=(
            "List of public repo names separated by commas in order of (pin) preference: 'owner/repo,owner/repo,...'. "
            "Overrules: --not_owned, --not_contributed, --pins (default), --order (default). "
            "Overruled by (when an arg is given): --pins, --order."
        ),
    )
    parser.add_argument(
        "--theme",
        type=str,
        default=THEME if THEME and len(THEME) > 0 else None,
        help=(
            "Repository pin image theme for all: 'theme'; or individual: {'repo': 'theme'}. Default: 'GitHub' theme."
        ),
    )
    parser.add_argument(
        "--pins",
        type=str,
        default=NUM_REPO_PINS if NUM_REPO_PINS else None,
        help="The maximum number of pinned repositories to fetch and display.",
    )
    parser.add_argument(
        "--order",
        type=str,
        choices=list(enums.RepositoryOrderFieldEnum.__members__.values()),
        default=(REPO_PIN_ORDER if REPO_PIN_ORDER else None),
        help="The order of repository data fetching from GitHub API and displaying of README pins where applicable.",
    )
    parser.add_argument(
        "--not-owned",
        type=bool,
        default=True if IS_EXCLUDE_REPOS_OWNED else False,
        help="If owned repositories are excluded from complementing pins.",
    )
    parser.add_argument(
        "--not-contributed",
        type=bool,
        default=True if IS_EXCLUDE_REPOS_CONTRIBUTED else False,
        help="If (not owned) repositories contributed to are excluded from complementing pins.",
    )
    args = parser.parse_args()

    exclusive_repo_name_pattern = compile(r"^\s*(?:,?\s*[\w.-]+/[\w.-]+\s*)*,?\s*$")
    assert (
        args.token is not None and isinstance(args.token, str) and len(args.token) > 0
    ), "A valid GitHub API token must be provided."
    assert args.username is None or (
        args.username is not None
        and isinstance(args.username, str)
        and len(args.username) > 0
    ), "A valid GitHub account username must be provided."
    assert (
        args.repos is None
        or isinstance(args.repos, str)
        and exclusive_repo_name_pattern.match(args.repos)
    ), "The exclusive list of repo names (owner/repo,owner/repo,..) must be in a single string and separated by commas."
    assert (
        args.pins is None or int(args.pins) and int(args.pins) > 0
    ), "The maximum number of pinned repositories must be an int value and greater than 0."
    assert (
        args.order is None
        or isinstance(args.order, str)
        and args.order.lower()
        in [
            e.value.lower()
            for e in list(enums.RepositoryOrderFieldEnum.__members__.values())
        ]
    ), (
        f"The repository order of preference must match one of: "
        f"{list(enums.RepositoryOrderFieldEnum.__members__.values())}"
    )

    if args.theme:
        try:
            args.theme = loads(s=args.theme)
        except (JSONDecodeError, TypeError):
            if not isinstance(args.theme, str):
                raise AssertionError(
                    "The repository theme must be either a string (for all repository pins) "
                    "or a dictionary (for individual repository pins)."
                )
            elif len(args.theme) == 0:
                args.theme = None

    return (
        args.token,
        args.username,
        args.repos,
        args.theme,
        args.pins,
        args.order,
        args.not_owned,
        args.not_contributed,
    )


def tst_svg_parse_args() -> tuple[str, str]:
    parser = ArgumentParser(description="Local test pin themes and SVG rendering.")
    parser.add_argument(
        "--theme",
        type=str,
        default="github_soft",
        help="A repo pin theme name, such as 'github', github_soft' or 'dracula', for examples.",
    )
    parser.add_argument(
        "--username",
        type=str,
        default="R055A",
        help="A GitHub account username.",
    )
    args = parser.parse_args()
    return args.theme.lower() if args.theme else args.theme, args.username


def init_logger() -> Logger:
    basicConfig(
        level=WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[StreamHandler(stdout)],
    )
    return getLogger("readme-repo-pins")


def set_git_creds(user_name: str, user_id: int) -> None:
    if getenv("GITHUB_ENV"):
        with open(file=getenv("GITHUB_ENV"), mode="a") as gh_env_file:
            gh_env_file.write(f"GH_USER_NAME={user_name}\n")
            gh_env_file.write(f"GH_USER_ID={user_id}\n")


def get_dir_path() -> str:
    if not Path("files").exists():
        return "../files"
    return "files"


def load_themes() -> dict[str, dict[str, dict[str, str]]]:
    with open(file=f"{get_dir_path()}/themes.json", mode="r") as themes_file:
        return load(themes_file)


def del_imgs() -> None:
    dir_name: str = get_dir_path()
    for filename in listdir(path=dir_name):
        file_path = path.join(dir_name, filename)
        if (
            filename.endswith(".svg")
            and path.isfile(path=file_path)
            or path.islink(path=file_path)
        ):
            unlink(path=file_path)
        elif path.isdir(s=file_path):
            rmtree(path=file_path)


def write_svg(svg_obj_str: str, file_name: str) -> None:
    with open(
        file=f"{get_dir_path()}/{file_name}.svg", mode="w", encoding="utf-8"
    ) as svg_file:
        svg_file.write(svg_obj_str)


def get_md_grid_pin_str(file_num: int, repo_name: str, repo_url: str) -> str:
    grid_str: str = ""
    if file_num % 2 == 0:
        grid_str += "\n"
    return (
        grid_str
        + f"[![{repo_name} pin img]({get_dir_path()}/{file_num}.svg)]({repo_url}) "
    )


def get_html_grid_pin_str(file_num: int) -> str:
    grid_str: str = ""
    if file_num % 2 == 0:
        grid_str += "\n"
    return (
        grid_str
        + f'<object type="image/svg+xml" data="{get_dir_path()}/{file_num}.svg"></object> '
    )


def update_md_file(update_pin_display_str: str, is_index_md: bool = False) -> None:
    readme_path: Path = Path("README.md" if not is_index_md else "index.md")
    update_data: str = sub(
        pattern=r"(<!-- START: REPO-PINS -->)(.*?)(<!-- END: REPO-PINS -->)",
        repl=rf"\1{update_pin_display_str}\n\3",
        string=readme_path.read_text(encoding="utf-8"),
        flags=DOTALL,
    )
    readme_path.write_text(data=update_data, encoding="utf-8")
