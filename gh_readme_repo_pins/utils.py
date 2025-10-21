from gh_readme_repo_pins.repo_pins_enum import RepositoryOrderFieldEnum
from argparse import ArgumentParser
from os import environ, getenv
from re import sub, DOTALL
from pathlib import Path

USERNAME: str = environ.get("GH_USERNAME", "")
GH_API_TOKEN: str = environ.get("GH_API_TOKEN", "")
NUM_REPO_PINS: str = environ.get("NUM_REPO_PINS", "")
REPO_PIN_ORDER: str = environ.get("REPO_PIN_ORDER", "")
IS_EXCLUDE_REPOS_OWNED: str = environ.get("IS_EXCLUDE_REPOS_OWNED", "")
IS_EXCLUDE_REPOS_CONTRIBUTED: str = environ.get("IS_EXCLUDE_REPOS_CONTRIBUTED", "")


def parse_args() -> tuple[str, str, int, str, bool, bool]:
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
        "--pins",
        type=str,
        default=NUM_REPO_PINS if NUM_REPO_PINS else None,
        help="The maximum number of pinned repositories to fetch and display.",
    )
    parser.add_argument(
        "--order",
        type=str,
        choices=list(RepositoryOrderFieldEnum.__members__.keys()),
        default=(
            REPO_PIN_ORDER
            if REPO_PIN_ORDER
            else RepositoryOrderFieldEnum.STARGAZERS.name
        ),
        help="The order of repository data fetching from GitHub API and displaying of README pins where applicable.",
    )
    parser.add_argument(
        "--not-owned",
        type=bool,
        default=True if IS_EXCLUDE_REPOS_OWNED else False,
        help="If owned repositories are excluded from complementing pins when too few.",
    )
    parser.add_argument(
        "--not-contributed",
        type=bool,
        default=True if IS_EXCLUDE_REPOS_CONTRIBUTED else False,
        help="If (not owned) repositories contributed to are excluded from complementing pins when too few.",
    )
    args = parser.parse_args()

    assert (
        args.token is not None and isinstance(args.token, str) and len(args.token) > 0
    ), "A valid GitHub API token must be provided."
    assert args.username is None or (
        args.username is not None
        and isinstance(args.username, str)
        and len(args.username) > 0
    ), "A valid GitHub account username must be provided."
    assert (
        args.pins is None or int(args.pins) and int(args.pins) > 0
    ), "The maximum number of pinned repositories must be greater than 0."
    assert (
        args.order
        and isinstance(args.order, str)
        and args.order in list(RepositoryOrderFieldEnum.__members__.keys())
    ), "The repository order of preference must match a valid RepositoryOrderField value."
    return (
        args.token,
        args.username,
        args.pins,
        args.order,
        args.not_owned,
        args.not_contributed,
    )


def set_git_creds(user_name: str, user_id: int) -> None:
    if getenv("GITHUB_ENV"):
        with open(file=getenv("GITHUB_ENV"), mode="a") as gh_env_file:
            gh_env_file.write(f"GH_USER_NAME={user_name}\n")
            gh_env_file.write(f"GH_USER_ID={user_id}\n")


def update_readme(update_pin_display_str: str):
    readme_path: Path = Path("README.md")
    def write_data_to_placeholder(marker: str, update_str: str = ""):
        update_data: str = sub(
            pattern=rf"(<!-- START: {marker.upper()} -->)(.*?)(<!-- END: {marker.upper()} -->)",
            repl=rf"\1{update_str}\n\3",
            string=readme_path.read_text(encoding="utf-8"),
            flags=DOTALL,
        )
        readme_path.write_text(data=update_data, encoding="utf-8")

    write_data_to_placeholder(
        marker="REPO-PINS", update_str=update_pin_display_str
    )
    write_data_to_placeholder(marker="TEMPLATE")
