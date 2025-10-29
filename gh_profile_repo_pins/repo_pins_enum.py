from sys import modules
from enum import Enum


class RepositoryOrderFieldEnum(Enum):
    STARGAZERS = "stargazerCount"
    NAME = "name"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    PUSHED_AT = "pushedAt"


class RepoPinsImgThemeName(Enum):
    GITHUB = "github"
    GITHUB_SOFT = "github_soft"


class RepoPinsImgThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"


def update_enum(enum_cls: type[Enum], enum_dict: dict[str, str]) -> None:
    updated_enum: Enum = Enum(
        enum_cls.__name__,
        {**{m.name: m.value for m in enum_cls}, **enum_dict},
        type=str,
        module=enum_cls.__module__,
    )
    setattr(modules[enum_cls.__module__], enum_cls.__name__, updated_enum)
