from sys import modules
from enum import Enum


class RepositoryOrderFieldEnum(Enum):
    STARGAZERS = "stargazerCount"
    NAME = "name"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    PUSHED_AT = "pushedAt"


class RepoPinsImgMediaBgImgMime(Enum):
    PNG = "image/png"
    JPG = "image/jpeg"
    SVG = "image/svg+xml"
    GIF = "image/gif"
    WEB = "image/webp"


class RepoPinsImgMediaBgImgAlignX(Enum):
    xMin = "xmin"
    xMid = "xmid"
    xMax = "xmax"


class RepoPinsImgMediaBgImgAlignY(Enum):
    YMin = "ymin"
    YMid = "ymid"
    YMax = "ymax"


class RepoPinsImgMediaBgImgAlign(Enum):
    xMinYMin = (
        RepoPinsImgMediaBgImgAlignX.xMin.value + RepoPinsImgMediaBgImgAlignY.YMin.value
    )
    xMinYMid = (
        RepoPinsImgMediaBgImgAlignX.xMin.value + RepoPinsImgMediaBgImgAlignY.YMid.value
    )
    xMinYMax = (
        RepoPinsImgMediaBgImgAlignX.xMin.value + RepoPinsImgMediaBgImgAlignY.YMax.value
    )
    xMidYMin = (
        RepoPinsImgMediaBgImgAlignX.xMid.value + RepoPinsImgMediaBgImgAlignY.YMin.value
    )
    xMidYMid = (
        RepoPinsImgMediaBgImgAlignX.xMid.value + RepoPinsImgMediaBgImgAlignY.YMid.value
    )
    xMidYMax = (
        RepoPinsImgMediaBgImgAlignX.xMid.value + RepoPinsImgMediaBgImgAlignY.YMax.value
    )
    xMaxYMin = (
        RepoPinsImgMediaBgImgAlignX.xMax.value + RepoPinsImgMediaBgImgAlignY.YMin.value
    )
    xMaxYMid = (
        RepoPinsImgMediaBgImgAlignX.xMax.value + RepoPinsImgMediaBgImgAlignY.YMid.value
    )
    xMaxYMax = (
        RepoPinsImgMediaBgImgAlignX.xMax.value + RepoPinsImgMediaBgImgAlignY.YMax.value
    )


class RepoPinsImgMediaBgImgMode(Enum):
    SLICE = "cover"
    MEET = "contain"
    NONE = "stretch"


class RepoPinsImgThemeName(Enum):
    GITHUB = "github"
    GITHUB_SOFT = "github_soft"
    BG_IMG_CONTRAST = "bg_img_contrast"
    DRACULA = "dracula"


class RepoPinsImgThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"


class RepoPinsStatsContributionData(Enum):
    DATA = "contribution_data"
    LOGIN = "login"
    STATS = "stats"


def update_enum(enum_cls: type[Enum], enum_dict: dict[str, str]) -> None:
    updated_enum: Enum = Enum(
        enum_cls.__name__,
        {**{m.name: m.value for m in enum_cls}, **enum_dict},
        type=str,
        module=enum_cls.__module__,
    )
    setattr(modules[enum_cls.__module__], enum_cls.__name__, updated_enum)
