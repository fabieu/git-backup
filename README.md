# git-backup

Backup all your repositories from GitHub and GitLab to your local filesystem. This script will automatically discover all projects based on a given personal access token and will clone them to the target path. If you rerun the script with the same target path specified it will update the repositories instead of cloning them again.

## Requirements

- Python 3.9 or higher
- Git (accessible in PATH)

## Installation

Clone this repository:

```bash
git clone https://github.com/fabieu/git-backup.git
```

Move into the cloned repository:

```bash
cd ./git-backup
```

Install the required dependencies in a virtual environment with pipenv:

```bash
python -m pip install pipenv
pipenv install --ignore-pipfile
pipenv shell
```

## Configuration

The configuration takes place via a config file named **_config.ini_**  
In the root path of the repository you can find a sample configuration file named _config.ini.sample_. It is recommended to rename the sample configuration and edit the necessary values.

**Example Configuration:**

```
[gitlab]
enabled = true
host = https://gitlab.com
personal_access_token = YOUR_PERSONAL_ACCESS_TOKEN
clone_method = http

[github]
enabled = true
host = https://api.github.com
personal_access_token = YOUR_PERSONAL_ACCESS_TOKEN
clone_method = http

[path]
target = repos
```

|          Key          |                                      Description                                       |    Section     |   Values    |
| :-------------------: | :------------------------------------------------------------------------------------: | :------------: | :---------: |
|        enabled        |                       Enable or disable the entire git platform                        | gitlab, github | true, false |
|         host          |              Github or GitLab API (defaults to github.com and gitlab.com)              | gitlab, github |             |
| personal_access_token |                         API token (view required scopes below)                         | gitlab, github |             |
|     clone_method      |                Git clone method (requires preconfigured authentication)                | gitlab, github |  ssh, http  |
|        target         | Absolute or relative path based on the script location for storing the repository data |      path      |             |

## Usage

Run the Python script:

```bash
python backup.py
```

## Licence

MIT License

Copyright (c) 2021 Fabian Eulitz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
