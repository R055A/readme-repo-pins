class RepoPinsException(Exception):

    def __init__(self, msg: str):
        self.msg: str = msg


class GitHubGraphQlClientError(RepoPinsException):

    def __init__(self, msg: str):
        super().__init__(msg=msg)


class RepoPinImageThemeError(RepoPinsException):

    def __init__(self, msg: str):
        super().__init__(msg=msg)


class RepoPinImageMediaError(RepoPinsException):

    def __init__(self, msg: str):
        super().__init__(msg=msg)


class RepoPinStatsError(RepoPinsException):

    def __init__(self, msg: str):
        super().__init__(msg=msg)
