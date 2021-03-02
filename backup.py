import requests
import git
import yaml
import logging
import sys
from pathlib import Path

# Global variables
config = None

# Basic Logging Config
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)s %(message)s'
)


def main():
    if config_valid():
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


# TODO: Implement strict validation
def config_valid():
    def config_error(attribut, message):
        logging.error(attribut + " : " + message)
        raise SystemExit(2)

    try:
        global config
        config = yaml.safe_load(open("config.yaml"))

        if not config["git"]["clone"] in ("ssh", "http"):
            config_error('git.clone', 'Wrong clone type in config.yaml specifed. Only "ssh" and "http" are allowed')

        return True

    except Exception as e:
        logging.exception()
        return False


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

    if config["git"]["clone"] == "ssh":
        clone_url = repo["clone_url_ssh"]
    elif config["git"]["clone"] == "http":
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
