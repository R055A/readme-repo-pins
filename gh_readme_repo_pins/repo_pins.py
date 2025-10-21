from gh_readme_repo_pins.repo_pins_enum import RepositoryOrderFieldEnum
from gh_readme_repo_pins.repo_pins_generate import GenerateRepoPins
from gh_readme_repo_pins.repo_pins_api_client import GitHubClient
from gh_readme_repo_pins.utils import set_git_creds


class ReadMeRepoPins:

    __DEFAULT_MAX_NUM_PINS: int = 6
    __DEFAULT_ORDER_FIELD: RepositoryOrderFieldEnum = (
        RepositoryOrderFieldEnum.STARGAZERS
    )

    def __init__(
        self,
        api_token: str,
        username: str = None,
        max_num_pins: int = None,
        repo_priority_order: str = None,
        is_exclude_repos_owned: bool = False,
        is_exclude_repos_contributed: bool = False,
    ) -> None:
        self.__gh_api_client: GitHubClient = GitHubClient(
            api_token=api_token, username=username
        )
        set_git_creds(
            user_name=self.__gh_api_client.user_name,
            user_id=self.__gh_api_client.user_id,
        )
        self.__repo_pins: list[dict] = list()
        self.__max_num_pins: int = (
            int(max_num_pins) if max_num_pins else self.__DEFAULT_MAX_NUM_PINS
        )
        self.__repo_priority_order: str = repo_priority_order
        self.__is_exclude_repos_owned: bool = is_exclude_repos_owned
        self.__is_exclude_repos_contributed: bool = is_exclude_repos_contributed

    def __order_repos_by_preference(
        self, repos: list[dict], order_field: str = None
    ) -> list[dict]:
        order_field: str = (
            getattr(RepositoryOrderFieldEnum, order_field, None).value
            if getattr(RepositoryOrderFieldEnum, order_field, None)
            else self.__DEFAULT_ORDER_FIELD.value
        )
        return sorted(
            repos,
            key=lambda d: next(
                (v for k, v in d.items() if order_field.upper() == k.upper()), 0
            ),
            reverse=(
                True
                if order_field.upper() != RepositoryOrderFieldEnum.NAME.value.upper()
                else False
            ),
        )

    def __generate_readme_pin_grid_display(self) -> None:
        gen_repo_pins: GenerateRepoPins = GenerateRepoPins(
            repo_pins_data=self.__repo_pins
        )
        gen_repo_pins.create_grid_display()

    def generate(self) -> None:
        self.__repo_pins: list[dict[str, str | int | dict[str, str]]] = (
            self.__gh_api_client.fetch_repo_pin_data()
        )
        if (
            len(self.__repo_pins) < self.__max_num_pins
            and not self.__is_exclude_repos_owned
        ):
            owned_repos: list[dict[str, str | int | dict[str, str]]] = (
                self.__order_repos_by_preference(
                    repos=self.__gh_api_client.fetch_repo_own_data(
                        order_field=self.__repo_priority_order,
                        pinned_repo_urls=[d["url"] for d in self.__repo_pins],
                    ),
                    order_field=self.__repo_priority_order,
                )[: self.__max_num_pins - len(self.__repo_pins)]
            )
            self.__repo_pins.extend(owned_repos)
        if (
            len(self.__repo_pins) < self.__max_num_pins
            and not self.__is_exclude_repos_contributed
        ):
            contributed_repos: list[dict[str, str | int | dict[str, str]]] = (
                self.__order_repos_by_preference(
                    repos=self.__gh_api_client.fetch_repo_contribute_data(
                        order_field=self.__repo_priority_order,
                        pinned_repo_urls=[d["url"] for d in self.__repo_pins],
                    ),
                    order_field=self.__repo_priority_order,
                )[: self.__max_num_pins - len(self.__repo_pins)]
            )
            self.__repo_pins.extend(contributed_repos)
        self.__generate_readme_pin_grid_display()
