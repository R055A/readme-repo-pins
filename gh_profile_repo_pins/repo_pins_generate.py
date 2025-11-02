from gh_profile_repo_pins.utils import (
    write_svg,
    del_imgs,
    update_md_file,
    load_themes,
    get_md_grid_pin_str,
    get_html_grid_pin_str,
)
from gh_profile_repo_pins.repo_pins_exceptions import RepoPinImageThemeError
from gh_profile_repo_pins.repo_pins_img_data import RepoPinImgData
from gh_profile_repo_pins.repo_pins_img_svg import RepoPinImg
import gh_profile_repo_pins.repo_pins_enum as enums


class GenerateRepoPins:

    def __init__(
        self,
        repo_pins_data: list[dict[str, str | int | bool | dict[str, str]]],
        username: str,
        theme: str | dict,
        bg_img: dict | str = None,
    ) -> None:
        self.update_themes()  # update the database with any new json themes not in enums.RepoPinsImgThemeName
        try:
            self.__repo_pins: list[RepoPinImgData] = [
                RepoPinImgData.format_repo_pin_data(
                    repo_data=i,
                    username=username,
                    theme_name=(
                        enums.RepoPinsImgThemeName(theme[i.get("name")])
                        if isinstance(theme, dict) and i.get("name") in theme
                        else (
                            enums.RepoPinsImgThemeName(theme)
                            if theme and not isinstance(theme, dict)
                            else None
                        )
                    ),
                    bg_img=(
                        bg_img.get(
                            [
                                j
                                for j in bg_img.keys()
                                if i.get("name") in j and j in i.get("url")
                            ][0]
                        )
                        if isinstance(bg_img, dict)
                        and bg_img.get(
                            [
                                j
                                for j in bg_img.keys()
                                if i.get("name") in j and j in i.get("url")
                            ][0]
                        ).get("img")
                        and any(
                            [
                                j
                                for j in bg_img.keys()
                                if i.get("name") in j and j in i.get("url")
                            ]
                        )
                        else (
                            bg_img
                            if isinstance(bg_img, dict)
                            and not isinstance(list(bg_img.values())[0], dict)
                            and bg_img.get("img")
                            else (
                                bg_img
                                if not isinstance(bg_img, dict)
                                and isinstance(bg_img, str)
                                and len(bg_img) > 0
                                else None
                            )
                        )
                    ),
                )
                for i in repo_pins_data
            ]
        except ValueError:
            raise RepoPinImageThemeError(
                msg=f"Theme '{theme}' is either not in themes.json or the database is not updated with the json data."
            )

    def __render_repo_pin_imgs(self) -> None:
        del_imgs()
        for i, repo_pin in enumerate(self.__repo_pins):
            repo_pin_img: RepoPinImg = RepoPinImg(repo_pin_data=repo_pin)
            repo_pin_img.render()
            write_svg(svg_obj_str=repo_pin_img.svg, file_name=str(i))

    def __build_grid(self, is_md_str: bool = True) -> str:
        grid_str: str = ""
        for i, repo_data in enumerate(self.__repo_pins):
            grid_str += (
                get_md_grid_pin_str(
                    file_num=i,
                    repo_name=repo_data.repo_name,
                    repo_url=repo_data.url,
                )
                if is_md_str
                else get_html_grid_pin_str(file_num=i)
            )
        return grid_str

    @classmethod
    def update_themes(cls) -> None:
        enums.update_enum(
            enum_cls=enums.RepoPinsImgThemeName,
            enum_dict={k.upper(): k for k in load_themes().keys()},
        )

    def grid_display(self) -> None:
        self.__render_repo_pin_imgs()
        update_md_file(update_pin_display_str=self.__build_grid())
        update_md_file(
            update_pin_display_str=self.__build_grid(is_md_str=False), is_index_md=True
        )
