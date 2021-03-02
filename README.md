# gitlab-backup

Constantly backup all your repositories from GitHub and/or GitLab to the local filesystem with a single Python script

## Requirements

- Python 3.9 or higher
- Git (accessible in PATH)

## Installation

Clone this repository to your machine

```bash
git clone https://github.com/fabieu/git-backup
```

Move into the cloned repository

```bash
cd ./git-backup
```

Install the required dependencies in a virtual environment:

```bash
python -m pip install pipenv
pipenv install
pipenv shell
```

## Usage

Run the Python script with

```bash
python backup.py
```

## Licence

MIT License

Copyright (c) 2021 Fabian Eulitz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
