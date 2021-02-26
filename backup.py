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
        projects = get_projects_gitlab()
        target_path = config["path"]["target"]

        if not Path(target_path).absolute().exists():
            Path(target_path).absolute().mkdir(parents=True, exist_ok=True)

        for project in projects:
            # If repository isn't located in the target path do a git clone --bare, otherwise update it via git remote update --prune
            repo_path = (Path(target_path) / Path(project["path"])).absolute()

            if Path(repo_path).exists():
                update_repo(repo_path, project)
            else:
                clone_repo(repo_path, project)


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


# Get all projects of the associated user based on membership - Reference: https://docs.gitlab.com/ee/api/projects.html#list-all-projects
def get_projects_gitlab():
    projects = []
    url = f'{config["gitlab"]["host"]}/api/v4/projects'
    headers = {'PRIVATE-TOKEN': config["gitlab"]["personal_access_token"]}
    payload = {
        'membership': True,
        'per_page': 50,
        'page': 1
    }

    while True:
        response = requests.get(url, headers=headers, data=payload)

        if response.ok:
            projects += response.json()

            if response.headers["x-next-page"]:
                payload["page"] = int(response.headers["x-next-page"])
            else:
                return projects

        else:
            logging.error(response.json())
            break


def clone_repo(repo_path, project):
    project_name = project["name_with_namespace"]

    if config["git"]["clone"] == "ssh":
        clone_url = project["ssh_url_to_repo"]
    elif config["git"]["clone"] == "http":
        clone_url = project["http_url_to_repo"]

    logging.info(f'Cloning {project_name} ({clone_url}) to {repo_path}')
    git.Repo.clone_from(clone_url, repo_path, bare=True)


def update_repo(repo_path, project):
    project_name = project["name_with_namespace"]

    logging.info(f'Updating {project_name} in {repo_path}')
    repo = git.repo.base.Repo(path=repo_path)
    git.remote.Remote(repo, 'origin').update(prune=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
