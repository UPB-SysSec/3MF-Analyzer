# About

This is project repository for our paper “Security Analysis of the 3MF Data Format”.

We created 3MF Analyzer to aid the automatic creation, execution, and evaluation of test cases.
The test cases are a mixture of manually and automatically create 3MF files.
The automatic test cases are created using the `create` command of the tool.
All resulting partial 3MF files and manually defined ones are bundled into 3MF archives (i.e. ZIPed) using the `build` command.

The `run` command starts a (to be tested) program and loads a 3MF file with the program.
It waits until the file is loaded and takes screenshots and program-state snapshots while doing so.
The `server` commands starts a servers that should be executed in parallel to the `run` command.

The `evaluate` and `gather` commands interpret the captured data and write them to readable Markdown (see `data/*.md`).

# Execution

The 3MF-Analyzer is a Python program and should be executed as a module.
That means when executing set the working directory to the `src` folder and run: `python -m 3mf-analyzer`.
All of the commands (besides `run`) run under Linux as well as Windows.  
*Please note*, that for the execution of the tested programs (using the `run` command) the program has to run natively on Windows.
The `create` command executes within a Docker container, but the paths of some test cases will be wrong.
This means, if you want to evaluate the programs, you have to execute `create`, `build`, and `run` on the Windows machine where the programs are installed.

## Setup

There are three ways in which you can run the tool.
For the `run` command and the manual GUI-mode for the `evaluate` command only the first option works.
The other options can be used to test the test case creation an evaluation.

1. **On the machine directly**:
   - Install Python Version 3.8 (newer versions *should* work but are not tested).
   - Make sure [Tk](https://tkdocs.com/index.html) is installed.
   - **Via Python Poetry** (only Python 3.8):
     - Install Python Poetry <https://python-poetry.org/>
     - Run `poetry install`
     - Run `poetry shell`
   - **Manually**:
     - Install the requirements in `.devcontainer/requirements.txt` either
       - globally `python38 -m pip install -r .devcontainer/requirements.txt` or
       - in a virtual environment.
          ```bash
          python38 -m venv .venv
          source .venv/bin/activate
          python38 -m pip install -r .devcontainer/requirements.txt
          ```
       assuming the Python Version 3.8 executable is called `python38`.
   - `cd src/`
2. **Docker using the .devcontainer**:
   - Install and setup [Docker](https://www.docker.com/).
   - Install [VS Code](https://code.visualstudio.com/) and the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
   - Run the `Remote-Containers: Reopen in Container` command in VS Code or follow the popup that appears when opening the repository using VS Code (with the extension installed).
   - `cd /workspace/3MF-Analyzer/src`
3. **Standalone Docker** (without using VS Code):
   - Install and setup [Docker](https://www.docker.com/).
   - Execute the following commands in the root directory of the repository:
     ```
     docker build \
       --file .devcontainer/Dockerfile \
       --tag 3mf-analyzer \
       .
     ```
     ```
     docker run \
       --rm -it \
       --entrypoint /bin/bash \
       --volume "$(pwd)/data:/workspace/data" \
       --volume "$(pwd)/src:/workspace/src" \
       3mf-analyzer
     ```
   - `cd /workspace/src`

Execute: `python -m 3mf-analyzer -h`

## Usage

In short, the following commands are available:

- **create**: Creates/Generates testcases into /data/testcases/{generated,server_files} (usually only required to run once on every system or if you change the generation code).
- **build**: Builds the existing testcases into the 3MF format.
- **run**: Runs the given test file(s) with the given program(s) (only Windows).
- **server**: Starts an HTTP Server. This should be executed in parallel to the run command (i.e. run `server` in a second terminal when you want to use `run`).
- **evaluate**: Evaluates the data produced by the run command.
- **gather**: Gathers the testcases and results into readable Markdown.

## Usage Notices for the `run` command

- Make sure submodules are pulled.
- Programs that you want to test have to be installed on the Windows machine and configured in `data/programs/config.yaml`.
  The `run` command can then execute them given their `id` as a CLI flag.
  - Make sure that the `type_association_id`'s of the different tested programs match on your installation.
    You can do so by setting the Default File Association in Windows (through the file explorer "Always open with {program}") and afterwards checking the set value with the PowerShell script in `src/PS-SFTA`:
    ```powershell
    cd src/PS-SFTA
    & { . .\SFTA.ps1; Get-FTA .3mf }
    ```
- Open the program(s) that you want to test prior to the test, adjust their size and move them to the primary monitor (if you have multiple monitors).
  The windows can be full screen, but this increases the execution time of the evaluation.
  We recommend you to drag the window in one corner of the screen (1/4th the size), as this is a reproducible scale (over multiple runs),
- You should avoid doing _ANYTHING_ on you machine while this runs.
  Unfortunately, the screenshot function is extremely brittle regarding focus etc.
  The problem is, that more reliable implementations wouldn't capture sub-windows (e.g. for error messages) so the implementation literally takes a screenshot of the area where the program's window is, even if it is not in the foreground.

# Repository Structure

- `data/` holds all the generated/written down information about the test cases, tested programs, and the results.
  Most of it can be generated into the `*.md` files in the `/data` directory with the `gather` command.
  - Test cases are defined in `data/testcases` (their build versions are stored in the gitignored `build` folder).
- `src/` contains the source code of the 3MF-Analyzer (`src/3mf-analyzer`) and other required libraries/scripts.

# Code Structure

Each command is contained in its own Python module (see the folders in `src/3mf-analyzer`).
Each module exports two functions `<module name>_parser` and `<module name>_main`.
The `*_parser` function exposes a CLI-argument parser, which's results are passed to the `*_main` function of the called command.
So to quickly understand the code you can open the `__init__.py` file in a module's folder and see which function is exported as the main entry point for the module.

# Misc

If you cannot push to GitHub based on its maximal file size of 100MB, try running

```
git lfs migrate import --above="100MB"
```

this will rewrite the **local** commits (make sure everything is committed) to use LFS for all files larger than 100MB.
