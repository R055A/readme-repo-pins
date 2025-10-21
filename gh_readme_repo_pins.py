from gh_readme_repo_pins.repo_pins import ReadMeRepoPins
from gh_readme_repo_pins.utils import parse_args


def gh_readme_repo_pins():
    custom_gh_readme_repo_pins: ReadMeRepoPins = ReadMeRepoPins(*parse_args())
    custom_gh_readme_repo_pins.generate()


if __name__ == "__main__":
    gh_readme_repo_pins()
