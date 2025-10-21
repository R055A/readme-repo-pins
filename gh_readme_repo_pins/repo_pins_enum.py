from enum import Enum


class RepositoryOrderFieldEnum(Enum):
    STARGAZERS = "stargazerCount"
    NAME = "name"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    PUSHED_AT = "pushedAt"
