from gh_profile_repo_pins.repo_pins_img_theme import RepoPinImgTheme, ThemeSVG
from gh_profile_repo_pins.repo_pins_img_data import RepoPinImgData
import gh_profile_repo_pins.repo_pins_enum as enums


class RepoPinImg:

    __SCALE: float = 1.0
    __WIDTH: float = round(400 * __SCALE)
    __HEIGHT: float = round(138 * __SCALE)
    __BASE_PADDING: int = 16
    __PADDING: float = round(__BASE_PADDING * __SCALE)
    __ROUNDING: float = round(6 * __SCALE)
    __NAME_SIZE: float = 14 * __SCALE
    __NAME_WEIGHT: int = 500
    __META_SIZE: float = 12 * __SCALE
    __DESC_SIZE: float = 12 * __SCALE
    __DESC_LINE_H: float = 1.35 * __DESC_SIZE

    __ICON_REPO: str = (
        "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 "
        "0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 "
        "1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 "
        ".25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"
    )
    __ICON_STAR: str = (
        "M8 12.027L3.33 14.5l.89-5.184L.5 5.763l5.165-.75L8 0"
        "l2.335 5.013 5.165.75-3.72 3.553.89 5.184L8 12.027z"
    )
    __ICON_FORK: str = (
        "M8 1a1.993 1.993 0 00-1 3.72V6L5 8 3 6V4.72A1.993 1.993 0 002 1a1.993 1.993 0 00-1 3.72V6.5l3 "
        "3v1.78A1.993 1.993 0 005 15a1.993 1.993 0 001-3.72V9.5l3-3V4.72A1.993 1.993 0 008 1zM2 4.2C1.34 "
        "4.2.8 3.65.8 3c0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2zm3 10c-.66 "
        "0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2 .65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2zm3-10c-.66 "
        "0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2z"
    )
    __ICON_FILL: str = "var(--fg-muted)"

    __BADGE_PUBLIC: str = "Public"
    __BADGE_ARCHIVE: str = " archive"
    __BADGE_TEMPLATE: str = " template"

    __MAX_STAT_NUMS: int = 1_000_000_000

    __WIDE_CHARS = set("mwMW@&%#$")
    __NARROW_CHARS = set("il!|:;.,`'")

    def __init__(self, repo_pin_data: RepoPinImgData) -> None:
        self.__repo_pin_data: RepoPinImgData = repo_pin_data
        self.__repo_pin_theme: dict[enums.RepoPinsImgThemeMode, ThemeSVG] = (
            RepoPinImgTheme(
                theme_name=self.__repo_pin_data.theme,
            ).svg_theme
        )
        self.__svg_str: str = ""

    def __theme_style_block(self) -> str | AttributeError:
        css: str = "<style>" + str(
            self.__repo_pin_theme.get(enums.RepoPinsImgThemeMode.LIGHT)
        )
        css += (
            "@media (prefers-color-scheme: dark) { "
            + str(self.__repo_pin_theme.get(enums.RepoPinsImgThemeMode.DARK))
            + " }"
        )
        return css + (
            """text { 
              font-family: -apple-system, 
              BlinkMacSystemFont, 
              "Segoe UI", 
              "Noto Sans", 
              Helvetica, 
              Arial, 
              sans-serif; 
            } 
          </style>"""
        )

    def __char_width(self, char: str, font_px: float) -> float:
        return font_px * (
            0.68
            if char in self.__WIDE_CHARS
            else (
                0.28 if char in self.__NARROW_CHARS else (0.33 if char == " " else 0.53)
            )
        )

    def __measure(self, txt: str, font_px: float) -> float:
        if not txt:
            return 0.0
        ttl: float = sum(self.__char_width(c, font_px) for c in txt)
        return max(0.0, ttl - min(ttl * 0.08, max(0, len(txt) - 1) * (0.02 * font_px)))

    def __truncate_to_width(self, txt: str, max_w: float) -> str:
        if self.__measure(txt=txt, font_px=self.__NAME_SIZE) <= max_w:
            return txt

        ell: str = "…"
        if self.__measure(txt=ell, font_px=self.__NAME_SIZE) > max_w:
            return ""

        start, end = 0, len(txt)
        while start < end:
            mid: float = (start + end + 1) // 2
            if self.__measure(txt=txt[:mid] + ell, font_px=self.__NAME_SIZE) <= max_w:
                start = mid
            else:
                end = mid - 1
        return (txt[:start] + ell) if start > 0 else ell

    def __header(self, repo_name_y: float) -> None:
        badge_txt: str = self.__BADGE_PUBLIC + (
            self.__BADGE_ARCHIVE
            if self.__repo_pin_data.is_archived
            else (self.__BADGE_TEMPLATE if self.__repo_pin_data.is_template else "")
        )
        badge_font_size: float = 10 * self.__SCALE
        badge_pad_x: float = round(6 * self.__SCALE)
        badge_w: float = (
            int(round(self.__measure(txt=badge_txt, font_px=badge_font_size) + 0.5))
            + badge_pad_x * 2
        )
        badge_h: float = round(badge_font_size + round(3 * self.__SCALE) * 2)

        name_badge_gap: float = round(8 * self.__SCALE)
        name_start_x: float = self.__PADDING + round(18 * self.__SCALE)
        max_name_w: float = (
            (self.__WIDTH - self.__PADDING)
            - name_start_x
            - name_badge_gap
            - badge_w
            - max(4.0, 7.0 * self.__SCALE, 0.3 * self.__NAME_SIZE)
        )
        display_name: str = self.__truncate_to_width(
            txt=f"{self.__repo_pin_data.repo_name}",
            max_w=max_name_w if max_name_w > 0 else 0,
        )

        self.__svg_str += (
            f"<a "
            f'href="{self.__repo_pin_data.url}" '
            f'target="_blank"'
            f">"
            f"<text "
            f'x="{name_start_x}" '
            f'y="{repo_name_y}" '
            f'font-size="{self.__NAME_SIZE}" '
            f'fill="var(--link)"'
            f">"
        )
        owner_repo: list[str] = display_name.split(sep="/", maxsplit=1)
        if len(owner_repo) > 1:
            self.__svg_str += f'<tspan font-weight="500">{owner_repo[0]}/</tspan>'
        self.__svg_str += f'<tspan font-weight="600">{owner_repo[-1]}</tspan>'
        self.__svg_str += "</text></a>"

        badge_x: float = min(
            name_start_x
            + self.__measure(txt=display_name, font_px=self.__NAME_SIZE)
            + name_badge_gap
            + max(4.0, 7.0 * self.__SCALE, 0.3 * self.__NAME_SIZE),
            (self.__WIDTH - self.__PADDING) - badge_w,
        )
        badge_y: float = repo_name_y - self.__NAME_SIZE * 0.35 - badge_h / 2

        self.__svg_str += (
            f'<g transform="translate({badge_x:.2f},{badge_y:.2f})">'
            f'<rect width="{badge_w}" '
            f'height="{badge_h}"'
            f' rx="{round(badge_h / 2)}" '
            f'ry="{round(badge_h / 2)}" '
            f'fill="var(--canvas)" '
            f'stroke="{"var(--danger-fg)" if self.__repo_pin_data.is_archived else "var(--border)"}"/>'
            f'<text x="{badge_pad_x}" '
            f'y="{round(badge_h / 2 + badge_font_size / 2) - 1}" '
            f'font-size="{badge_font_size}" '
            f'fill="{"var(--danger-fg)" if self.__repo_pin_data.is_archived else "var(--fg-muted)"}" '
            f'textLength="{badge_w - 2 * badge_pad_x}" '
            f'lengthAdjust="spacingAndGlyphs">'
            f"{badge_txt}"
            f"</text>"
            f"</g>"
        )

    def __wrap_lines(self, max_width_px: float, area_height_px: float) -> list[str]:
        if (
            not self.__repo_pin_data.description
            or (area_height_px - self.__DESC_SIZE) < -1e-6
        ):
            return []

        max_lines: int = max(
            0,
            min(
                3,
                1
                + max(
                    0, int((area_height_px - self.__DESC_SIZE) // self.__DESC_LINE_H)
                ),
            ),
        )
        words: list[str] = self.__repo_pin_data.description.strip().split(" ")
        lines: list[str] = []
        cur_line: str = ""
        for word in words:
            tmp_line = (cur_line + " " + word).strip() if cur_line else word
            if self.__measure(txt=tmp_line, font_px=self.__DESC_SIZE) <= max_width_px:
                cur_line = tmp_line
            elif cur_line:
                lines.append(cur_line)
                cur_line = word
            else:
                part_word: str = ""
                for char in word:
                    if (
                        self.__measure(txt=part_word + char, font_px=self.__DESC_SIZE)
                        <= max_width_px
                    ):
                        part_word += char
                    else:
                        break
                lines.append(part_word or word[:1])
                cur_line = word[len(part_word) :].lstrip()

            if len(lines) == max_lines:
                break

        if cur_line and len(lines) < max_lines:
            lines.append(cur_line)

        if len(lines) > max_lines:
            lines = lines[:max_lines]

        if lines:
            last_word: str = lines[-1]
            ell: str = "…"
            if self.__measure(txt=last_word, font_px=self.__DESC_SIZE) > max_width_px:
                while (
                    last_word
                    and self.__measure(txt=last_word + ell, font_px=self.__DESC_SIZE)
                    > max_width_px
                ):
                    last_word = last_word[:-1]
                lines[-1] = (last_word + ell) if last_word else ell
            elif len(" ".join(lines)) < len(" ".join(words)):
                if (
                    self.__measure(txt=last_word + ell, font_px=self.__DESC_SIZE)
                    <= max_width_px
                ):
                    lines[-1] = last_word + ell
                else:
                    while (
                        last_word
                        and self.__measure(
                            txt=last_word + ell, font_px=self.__DESC_SIZE
                        )
                        > max_width_px
                    ):
                        last_word = last_word[:-1]
                    lines[-1] = (last_word + ell) if last_word else ell
        return lines

    def __parent_repo(self):
        pass  # TODO

    def __description(self, repo_name_y: float, description_y: float) -> None:
        if self.__repo_pin_data.is_fork and self.__repo_pin_data.parent:
            self.__parent_repo()  # TODO

        wrapped_description_lines: list[str] = self.__wrap_lines(
            max_width_px=(self.__WIDTH - 2 * self.__PADDING),
            area_height_px=max(
                0.0, (description_y - self.__PADDING) - (repo_name_y + self.__PADDING)
            ),
        )
        for i, line in enumerate(wrapped_description_lines):
            line = (
                line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;")
            )
            self.__svg_str += (
                f"<text "
                f'x="{self.__PADDING}" '
                f'y="{((repo_name_y + self.__PADDING) + self.__DESC_SIZE) + (i * self.__DESC_LINE_H):.2f}" '
                f'font-size="{self.__DESC_SIZE}" '
                f'fill="var(--fg-muted)"'
                f">"
                f"{line}"
                f"</text>"
            )

    def __render_icon(
        self, path_d: str, x: float, y: float, size: float, is_star: bool = False
    ) -> str:
        return (
            f"<g "
            f'transform="translate({x:.2f},{y:.2f}) '
            f'scale({size / self.__BASE_PADDING:.4f})"'
            f">"
            f"<path "
            f'd="{path_d}" '
            f'fill="{"none" if is_star else self.__ICON_FILL}" '
            f'stroke="{self.__ICON_FILL if is_star else "none"}" '
            f'stroke-width="{1.4 if is_star else 0}" '
            f'fill-rule="evenodd"'
            f"/>"
            f"</g>"
        )

    def __fmt_footer_stats_str(self, stats_count: int) -> str:
        return (
            f"{stats_count / self.__MAX_STAT_NUMS:.1f}B".rstrip("0").rstrip(".")
            if stats_count >= self.__MAX_STAT_NUMS
            else (
                f"{stats_count / (self.__MAX_STAT_NUMS / 1_000):.1f}M".rstrip(
                    "0"
                ).rstrip(".")
                if stats_count >= (self.__MAX_STAT_NUMS / 1_000)
                else (
                    f"{stats_count / (self.__MAX_STAT_NUMS / 1_000_000):.1f}k".rstrip(
                        "0"
                    ).rstrip(".")
                    if stats_count >= (self.__MAX_STAT_NUMS / 1_000_000)
                    else str(stats_count)
                )
            )
        )

    def __footer_stats(
        self,
        stats_icon: str,
        stats_count: int,
        footer_x: float,
        footer_y: float,
        is_star: bool = False,
        icon_size: float = 13 * __SCALE,
        footer_top: float = 0.0,
        footer_h: float = 0.0,
        icon_y_adj: float = 0.0,
    ) -> float:
        if stats_count <= 0:
            return footer_x

        txt: str = self.__fmt_footer_stats_str(stats_count=stats_count)
        icon_txt_gap: float = round(15 * self.__SCALE)
        txt_w: float = self.__measure(txt=txt, font_px=self.__META_SIZE)
        self.__svg_str += (
            f'<a href="{f'{self.__repo_pin_data.url}/{"stargazers" if is_star else "forks"}'}" target="_blank">'
            f"<g>"
            f"<rect "
            f'x="{footer_x:.2f}" '
            f'y="{footer_top:.2f}" '
            f'width="{icon_txt_gap + txt_w:.2f}" '
            f'height="{footer_h:.2f}" '
            f'fill="transparent" '
            f'pointer-events="all" '
            f'style="cursor:pointer;" '
            f"/>"
            f"{self.__render_icon(
                path_d=stats_icon, 
                x=footer_x,
                y=footer_top + (footer_h - icon_size) / 2 + icon_y_adj, 
                size=icon_size, 
                is_star=is_star
            )}"
            f"<text "
            f'x="{footer_x + icon_txt_gap:.2f}" '
            f'y="{footer_y:.2f}" '
            f'font-size="{self.__META_SIZE}" '
            f'fill="var(--fg-muted)">'
            f"{txt}"
            f"</text>"
            f"</g>"
            f"</a>"
        )
        return footer_x + (icon_txt_gap + txt_w) + round(14 * self.__SCALE)

    def __footer(self, footer_y: float, footer_top: float, footer_h: float) -> None:
        footer_x: float = self.__PADDING

        if self.__repo_pin_data.primary_language_name:
            circle_cx: float = self.__PADDING + round(7 * self.__SCALE)
            self.__svg_str += (
                f"<circle "
                f'cx="{circle_cx}" '
                f'cy="{footer_top + footer_h / 2 - 0.5}" '
                f'r="{round(7 * self.__SCALE)}" '
                f'fill="{self.__repo_pin_data.primary_language_color}"'
                f"/>"
            )

            txt_x: float = circle_cx + round(7 * self.__SCALE) + round(6 * self.__SCALE)
            self.__svg_str += (
                f"<text "
                f'x="{txt_x}" '
                f'y="{footer_y}" '
                f'font-size="{self.__META_SIZE}" '
                f'fill="var(--fg-muted)"'
                f">"
                f"{self.__repo_pin_data.primary_language_name}"
                f"</text>"
            )

            footer_x = (
                txt_x
                + self.__measure(
                    txt=self.__repo_pin_data.primary_language_name,
                    font_px=self.__META_SIZE,
                )
                + round(14 * self.__SCALE)
            )
        footer_x = self.__footer_stats(
            stats_icon=self.__ICON_STAR,
            stats_count=self.__repo_pin_data.stargazer_count,
            footer_x=footer_x,
            footer_y=footer_y,
            is_star=True,
            icon_size=13 * self.__SCALE,
            footer_top=footer_top,
            footer_h=footer_h,
            icon_y_adj=-0.5,
        )
        self.__footer_stats(
            stats_icon=self.__ICON_FORK,
            stats_count=self.__repo_pin_data.fork_count,
            footer_x=footer_x,
            footer_y=footer_y,
            icon_size=13 * self.__SCALE,
            footer_top=footer_top,
            footer_h=footer_h,
            icon_y_adj=0.0,
        )

    def __render_svg(self) -> None:
        repo_name_y: float = self.__PADDING + self.__NAME_SIZE
        footer_h: float = max((13 * self.__SCALE), self.__META_SIZE)
        description_y: float = (self.__HEIGHT - self.__PADDING) - footer_h
        footer_y: float = description_y + (footer_h / 2) + (0.35 * self.__META_SIZE)

        self.__svg_str = f"""<?xml version="1.0" encoding="UTF-8"?>
        <svg 
          width="{self.__WIDTH}" 
          height="{self.__HEIGHT}" 
          viewBox="0 0 {self.__WIDTH} {self.__HEIGHT}" 
          xmlns="http://www.w3.org/2000/svg" 
          role="img" 
          aria-label="{self.__repo_pin_data.repo_name}"
        >
          <title>{self.__repo_pin_data.repo_name}</title>
          {self.__theme_style_block()}
          <defs><clipPath id="clip"><rect 
            x="0" 
            y="0" 
            width="{self.__WIDTH}" 
            height="{self.__HEIGHT}" 
            rx="{self.__ROUNDING}" 
            ry="{self.__ROUNDING}"
          /></clipPath></defs>
          <g clip-path="url(#clip)">
            <rect 
              x="0" 
              y="0" 
              width="{self.__WIDTH}" 
              height="{self.__HEIGHT}" 
              fill="var(--canvas)" 
              stroke="var(--border)"
            />
            {self.__render_icon(
                path_d=self.__ICON_REPO, 
                x=self.__PADDING, 
                y=repo_name_y - (self.__NAME_SIZE * 0.79) + 0.5 * self.__SCALE,
                size=14 * self.__SCALE,
            )}
        """

        self.__header(repo_name_y=repo_name_y)
        self.__description(repo_name_y=repo_name_y, description_y=description_y)
        self.__footer(footer_y=footer_y, footer_top=description_y, footer_h=footer_h)

        self.__svg_str += f"""
          </g>
          <rect 
            x="0.5" 
            y="0.5" 
            width="{self.__WIDTH - 1}" 
            height="{self.__HEIGHT - 1}" 
            rx="{self.__ROUNDING}" 
            ry="{self.__ROUNDING}" 
            fill="none" 
            stroke="var(--border)"
          />
        </svg>
        """

    @property
    def data(self) -> RepoPinImgData:
        return self.__repo_pin_data

    @property
    def svg(self) -> str:
        return self.__svg_str

    def render(self) -> None:
        self.__render_svg()


def tst_svg_render() -> None:
    from gh_profile_repo_pins.repo_pins_exceptions import RepoPinImageThemeError
    from gh_profile_repo_pins.repo_pins_generate import GenerateRepoPins
    from gh_profile_repo_pins.utils import write_svg

    GenerateRepoPins.update_themes()  # update the database with any new json themes not in enums.RepoPinsImgThemeName

    test_theme_name: str = "github"
    test_username: str = "R055A"
    tst_input: list[dict[str, str | int | bool | dict[str, str]]] = [
        {
            "name": "readme-repo-pins",
            "stargazerCount": 110_000,
            "forkCount": 9_900_000_000,
            "owner": {"login": "profile-icons"},
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
            "nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in "
            "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
            "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
            "culpa qui officia deserunt mollit anim id est laborum.",
            "url": "https://github.com/profile-icons/readme-repo-pins",
            "primaryLanguage": {"name": "MATLAB", "color": "#e16737"},
            "isFork": True,
            "parent": {"nameWithOwner": "R055A/readme-repo-pins"},
            "isTemplate": True,
            "isArchived": True,
        },
        {
            "name": test_username,
            "stargazerCount": 0,
            "forkCount": 1,
            "owner": {"login": test_username},
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "url": f"https://github.com/{test_username}/{test_username}",
            "primaryLanguage": {"name": "Python", "color": "#3572A5"},
            "isFork": False,
            "parent": {},
            "isTemplate": True,
            "isArchived": False,
        },
        {
            "name": "readme-repo-pins-readme-repo-pins",
            "stargazerCount": 0,
            "forkCount": 0,
            "owner": {"login": "profile-icons"},
            "description": "",
            "url": "https://github.com/profile-icons/readme-repo-pins",
            "primaryLanguage": {},
            "isFork": False,
            "parent": {},
            "isTemplate": False,
            "isArchived": False,
        },
    ]

    try:
        for i, tst_repo_data in enumerate(tst_input):
            repo_pin: RepoPinImgData = RepoPinImgData.format_repo_pin_data(
                repo_data=tst_repo_data,
                username=test_username,
                theme_name=enums.RepoPinsImgThemeName(test_theme_name),
            )
            repo_pin_img: RepoPinImg = RepoPinImg(repo_pin_data=repo_pin)
            repo_pin_img.render()
            write_svg(svg_obj_str=repo_pin_img.svg, file_name=f"-{i + 1}")
    except ValueError:
        print(
            f"Theme '{test_theme_name}' is either not in themes.json or GenerateRepoPins.update_themes() is not used."
        )
    except RepoPinImageThemeError as err:
        print(err.msg)


if __name__ == "__main__":
    tst_svg_render()
