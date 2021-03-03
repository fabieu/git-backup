import requests
import git
import logging
import sys
from pathlib import Path
from configparser import ConfigParser

# Global variables
config = None

# Basic Logging Config
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)s %(message)s'
)


class InvalidConfig(Exception):
    pass


class ConfigValidator(ConfigParser):
    def __init__(self, config_file):
        super(ConfigValidator, self).__init__()

        self.config_file = config_file
        self.read(config_file)
        self.validate_config()

    def validate_config(self):
        required_values = {
            'gitlab': {
                'enabled': ('true', 'false'),
                'host': None,
                'personal_access_token': None,
                'clone_method': ('http', 'ssh')
            },
            'github': {
                'enabled': ('true', 'false'),
                'host': None,
                'personal_access_token': None,
                'clone_method': ('http', 'ssh')
            },
            'path': {
                'target': None
            }
        }

        for section, keys in required_values.items():
            if section not in self:
                raise InvalidConfig(
                    f'{self.__class__.__name__}: Missing section "{section}" in {self.config_file}')

            for key, values in keys.items():
                if key not in self[section] or self[section][key] in ('', 'YOUR_PERSONAL_ACCESS_TOKEN'):
                    raise InvalidConfig(
                        f'{self.__class__.__name__}: Missing value for "{key}" in section "{section}" in {self.config_file}')

                if values:
                    if self[section][key] not in values:
                        allowed_values = "[{0}]".format(', '.join(map(str, values)))
                        raise InvalidConfig(
                            f'{self.__class__.__name__}: Invalid value for "{key}" under section "{section}" in {self.config_file} - allowed values are {allowed_values}')


def main():
    validate_config()
    repos = get_repositories()
    target_path = Path(config["path"]["target"]).absolute()

    # Create target path if it doesnt exist
    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)

    for repo in repos:
        # Determine the path for individual repositories based on the target path
        repo_path = (target_path / Path(f'{repo["platform"]}_{repo["path"]}')).absolute()

        # If repository isn't located in the target path do a git clone --bare, otherwise update it via git remote update --prune
        if repo_path.exists():
            update_repo(repo_path, repo)
        else:
            clone_repo(repo_path, repo)


def validate_config():
    try:
        global config
        config = ConfigValidator('config.ini')

    except InvalidConfig as e:
        logging.error(e)
        raise SystemExit(2)


def get_repositories():
    gitlab_enabled = config["gitlab"]["enabled"]
    github_enabled = config["github"]["enabled"]

    repositories = []

    if gitlab_enabled:
        repositories += get_repositories_gitlab()

    if github_enabled:
        repositories += get_repositories_github()

    return repositories


# Get all GitLab projects of the associated user - Reference: https://docs.gitlab.com/ee/api/projects.html#list-all-projects
def get_repositories_gitlab():
    repos = []
    page = 1

    # GitLab API Configuration
    gitlab_api_host = config["gitlab"]["host"]
    gitlab_api_token = config["gitlab"]["personal_access_token"]

    # GitLab API Pagination Loop
    while True:
        try:
            response = requests.get(
                f'{gitlab_api_host}/api/v4/projects',
                headers={
                    'PRIVATE-TOKEN': gitlab_api_token
                },
                data={
                    'membership': True,
                    'per_page': 100,
                    'page': page
                }
            )
            response.raise_for_status()

            # Build custom repo object from API response for further processing
            for instance in response.json():
                repo = dict()
                repo["platform"] = "gitlab"
                repo["name"] = instance["name"].strip()
                repo["path"] = instance["path"]
                repo["web_url"] = instance["web_url"]
                repo["clone_url_ssh"] = instance["ssh_url_to_repo"]
                repo["clone_url_http"] = instance["http_url_to_repo"]
                repo["clone_method"] = config["gitlab"]["clone_method"]
                repos.append(repo)

            if response.headers["x-next-page"]:
                page = int(response.headers["x-next-page"])
            else:
                if len(repos) == 0:
                    obfuscated_api_token = gitlab_api_token[-8:].rjust(len(gitlab_api_token), '*')
                    logging.warning(f'No repositories found for the personal access token {obfuscated_api_token}')
                    sys.exit()
                else:
                    return repos

        except requests.exceptions.HTTPError as e:
            logging.error(e)
            raise SystemExit()


# Get all GitHub projects of the associated user - Reference: https://docs.github.com/en/rest/reference/repos#list-repositories-for-the-authenticated-user
def get_repositories_github():
    repos = []
    page = 1

    # GitHub API Configuration
    github_api_host = config["github"]["host"]
    github_api_token = config["github"]["personal_access_token"]

    # GitHub API Pagination Loop
    while True:
        try:
            response = requests.get(
                f'{github_api_host}/user/repos',
                headers={
                    'Authorization': f'token {github_api_token}'
                },
                params={
                    'per_page': 100,
                    'page': page
                }
            )
            response.raise_for_status()

            # Build custom repo object from API response for further processing
            for instance in response.json():
                repo = dict()
                repo["platform"] = "github"
                repo["name"] = instance["name"].strip()
                repo["path"] = instance["name"]
                repo["web_url"] = instance["html_url"]
                repo["clone_url_ssh"] = instance["ssh_url"]
                repo["clone_url_http"] = instance["clone_url"]
                repo["clone_method"] = config["github"]["clone_method"]
                repos.append(repo)

            if len(response.json()) != 0:
                page = page + 1
            else:
                if len(repos) == 0:
                    obfuscated_api_token = github_api_token[-8:].rjust(len(github_api_token), '*')
                    logging.warning(f'No repositories found for the personal access token {obfuscated_api_token}')
                    sys.exit()
                else:
                    return repos

        except requests.exceptions.HTTPError as e:
            logging.error(e)
            raise SystemExit()


def clone_repo(repo_path, repo):
    repo_name = repo["name"]

    if repo["clone_method"] == "ssh":
        clone_url = repo["clone_url_ssh"]
    elif repo["clone_method"] == "http":
        clone_url = repo["clone_url_http"]

    logging.info(f'Cloning {repo_name} ({clone_url}) to {repo_path}')
    git.Repo.clone_from(clone_url, repo_path, bare=True)


def update_repo(repo_path, repo):
    repo_name = repo["name"]

    logging.info(f'Updating {repo_name} to {repo_path}')
    git_repo = git.repo.base.Repo(path=repo_path)
    git.remote.Remote(git_repo, 'origin').update(prune=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
