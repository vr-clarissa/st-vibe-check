# Support Ticket Vibe Check
A tool for tracking overall customer sentiment across submitted support tickets.  

## Prerequisites
1. Install python 3.12, [pyenv](https://github.com/pyenv/pyenv) is recommended to manage multiple python versions via command line.
2. Install `pdm` by running `pip install pdm`. This is what we use to install dependencies instead of `pip`, which helps us get more deterministic builds.

## Getting setup
1. At root directory of this project, install all required packages by running
    ```bash
    pdm install --dev
    ```
    This will take a while the first time because it's resolving all the dependencies from the `pdm.lock`. It will install all the dependencies to the root project directory like this: `st-vibe-check/.venv`
2. To run tools or scripts within the `pdm` virtual environment, prefix your commands with `pdm run`. If you'd like to activate the virtual environment for your entire shell session, use: `eval $(pdm venv activate)`. 
3. Add a .env file to your base folder st-vibe-check 
   - Add the python path `export PYTHONPATH=$PYTHONPATH:${PWD}` to the env file
4. [Optional] Install the precommit Git hook by running
    ```bash
    brew install pre-commit
    pre-commit install
    ```
    This will get Black formatter and flake8 checker triggered on every commit you make to format and lint your code. You may benefit from integrating black and flake8 into your IDE of choice.
