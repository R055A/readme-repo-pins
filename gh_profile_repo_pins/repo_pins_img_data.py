from gh_profile_repo_pins.repo_pins_exceptions import RepoPinImageMediaError
from gh_profile_repo_pins.repo_pins_img_media import RepoPinImgMedia
import gh_profile_repo_pins.repo_pins_enum as enums
from dataclasses import dataclass


@dataclass(frozen=True)
class RepoPinImgData:
    repo_name: str
    stargazer_count: int
    fork_count: int
    description: str
    url: str
    primary_language_name: str
    primary_language_color: str
    is_fork: bool
    parent: str
    is_template: bool
    is_archived: bool
    theme: enums.RepoPinsImgThemeName
    bg_img: RepoPinImgMedia

    @classmethod
    def format_repo_pin_data(
        cls,
        repo_data: dict,
        username: str,
        theme_name: enums.RepoPinsImgThemeName = enums.RepoPinsImgThemeName.GITHUB_SOFT,
        bg_img: dict | str = None,
    ) -> "RepoPinImgData":
        repo_owner = (
            repo_data.get("url", "").split("/")[-2]
            if len(repo_data.get("url", "").split("/")) > 1
            else ""
        )
        repo_parent = (
            repo_data.get("parent", {}).get("nameWithOwner", "") or ""
            if repo_data.get("parent", {})
            else None
        )
        primary_language_dict = repo_data.get("primaryLanguage", {}) or {}

        try:
            bg_img = (
                (
                    RepoPinImgMedia(**bg_img)
                    if isinstance(bg_img, dict)
                    else RepoPinImgMedia(img=bg_img)
                )
                if bg_img
                and (
                    isinstance(bg_img, dict)
                    and bg_img.get("img")
                    or isinstance(bg_img, str)
                )
                else None
            )
        except ValueError as err:
            raise RepoPinImageMediaError(msg=f"Background image error: {str(err)}")

        return RepoPinImgData(
            repo_name=(
                f"{repo_owner}/" if username.lower() != repo_owner.lower() else ""
            )
            + repo_data.get("name", ""),
            stargazer_count=repo_data.get("stargazerCount", 0) or 0,
            fork_count=repo_data.get("forkCount", 0) or 0,
            description=repo_data.get("description", "") or "",
            url=repo_data.get("url", "") or "",
            primary_language_name=primary_language_dict.get("name", "") or "",
            primary_language_color=primary_language_dict.get("color", "") or "",
            is_fork=repo_data.get("isFork", False) or "",
            parent=repo_parent,
            is_template=repo_data.get("isTemplate", False) or False,
            is_archived=repo_data.get("isArchived", False) or False,
            theme=(
                theme_name
                if theme_name
                else (
                    enums.RepoPinsImgThemeName.BG_IMG_CONTRAST
                    if bg_img
                    else enums.RepoPinsImgThemeName.GITHUB_SOFT
                )
            ),
            bg_img=bg_img,
        )

    def __repr__(self) -> str:
        return (
            f"name: {self.repo_name}\n"
            f"type: Public{" archive" if self.is_archived else (" template" if self.is_template else "")}"
            f"{"" if not self.is_fork else f"\nforked from {self.parent}"}"
            f"{f"\ndescription: {self.description}" if self.description else ""}"
            f"{f"\nprimary language: ({self.primary_language_color}) {self.primary_language_name}"
            if self.primary_language_name else ""}"
            f"{f"\nstargazers: {self.stargazer_count}" if self.stargazer_count else ""}"
            f"{f"\nforks: {self.fork_count}" if self.fork_count else ""}"
            f"\ntheme: {self.theme.value if self.theme else "None"}"
            f"\nbackground image: {f"\n{str(self.bg_img)}" if self.bg_img else "None\n"}"
        )
