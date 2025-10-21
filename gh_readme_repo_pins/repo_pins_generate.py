from gh_readme_repo_pins.utils import update_readme


class GenerateRepoPins:

    def __init__(self, repo_pins_data: list[dict]) -> None:
        self.__repo_pins: list[dict] = repo_pins_data

    def __generate_repo_pin_images(self) -> str:
        dynamic_repo_pins: str = str()
        for i, pinned_repo in enumerate(self.__repo_pins):
            dynamic_repo_pins += f"""\n{i + 1}. {pinned_repo}"""
        return dynamic_repo_pins

    def create_grid_display(self) -> None:
        update_readme(update_pin_display_str=self.__generate_repo_pin_images())
