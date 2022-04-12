# Overview

- Test cases are defined in `src/testcases` (their build versions are stored in the gitignored `build` folder).
- `src/testbed` holds a program to automate a number of tasks (execute with: `cd src; python -m testbed`).
  Most of them (besides the `run` command) run under Linux as well as Windows.
- Data holds all the generated/written down information about the test cases, tested programs, and the results.
  Most of it can be generated into the `*.md` files in the `/data` directory with the `gather` command.
- This project used Python Poetry <https://python-poetry.org/> for all the requirements, etc.
  You can either install Poetry (is restricted to Python 3.8, as that is what is most commonly available) or install the requirements that are generated by poetry for the `.devcontainer` (I hopefully have them always up-to-date).

## Usage Notices for the `run` command

- Make sure submodules are pulled.
- Make sure that the `type_association_id`'s are universal (and not just local to my installation) (see: `data/programs/config.yaml`).
  You can do so by setting the Default File Association in Windows (through the file explorer "Always open with {program}") and afterwards checking the set value with the PowerShell script in `src/PS-SFTA`:
  ```powershell
  cd src/PS-SFTA
  & { . .\SFTA.ps1; Get-FTA .3mf }
  ```
- Open the program(s) that you want to test prior to the test, make them fullscreen and move them to the primary monitor (if you have multiple monitors).
  Programs usually remember those values and various CLI flags or Python bindings work astonishingly unreliable.
- You should avoid doing _ANYTHING_ on you machine while this runs.
  Unfortunately, the screenshot function is extremely brittle regarding focus etc.
  The problem is, that more reliable implementations wouldn't capture sub-windows (e.g. for error messages) so the implementation literally takes a screenshot of the area where the program's window is, even if it is not in the foreground.

## Test Cases

The `src/testcases` folder has the files in unzipped form (if possible/required).
If a folder in `src/testcases` has one or multiple "file endings" (e.g. `test.3mf`, `test.xyz.zip`) then those suffixes are considered the type of files build from the folder.
Simply put, one can add any type of file as long as it is implemented in the `run` command (`build_file_from_folder` function).

The `.3mf` ending simply zips the folder and outputs it as a 3MF file.
The `.3mf_models` ending allows multiple `.model` files to be in the root of the directory which will be put as `/3D/3dmodel.model` in a basic 3MF file (described by the `skeleton` folder).
Files are simply copied.
Folders without a type are used for nesting/organization.

To run the script use Python 3.9 (I guess 3.8 would work as well, but I'm not sure) and make sure to run it from this directory.
If something went wrong the script will try to tell you the name of the file involved in the error.

# Misc

If you cannot push to HitHub based on its maximal file size of 100MB, try running

```
git lfs migrate import --above="100MB"
```

this will rewrite the **local** commits (make sure everything is committed) to use LFS for all files larger than 100MB.
