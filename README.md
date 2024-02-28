shellcheck-gha
==============

![PyPI Project Version](https://img.shields.io/pypi/v/shellcheck-gha.svg)
![Supported Python Versions](https://img.shields.io/pypi/pyversions/shellcheck-gha.svg)
![Project Python Implementations](https://img.shields.io/pypi/implementation/shellcheck-gha.svg)

This Python script extracts shell scripts from GitHub workflows
(`jobs.<job_id>.steps[*].run`) and runs them against [ShellCheck].

## Installation

**Requirements:**

- Python ≥ 3.11
- [ShellCheck] ≥ 0.9.0, available on `apt`, `brew`, `cabal`, `dnf`, and `pkg`.

### PyPI (prefered)

The project is hosted on PyPI at https://pypi.org/project/shellcheck-gha/.
To install the project, run:

```
$ pip install shellcheck-gha
```

### From Source

Alternatively, the project can be cloned and installed using [poetry].

```
$ git clone https://github.com/saleor/shellcheck-gha
$ pip install poetry
$ poetry install
$ shellcheck-gha --help
```

## Usage

```
$ shellcheck-gha --help
usage: shellcheck-gha [-h] [--default-shell DEFAULT_SHELL] [--verbose] [--debug] directory

positional arguments:
  directory

options:
  -h, --help            show this help message and exit
  --default-shell DEFAULT_SHELL
                        The default shell running in the workflow(s)
  --verbose             Show more details about the execution.
  --debug               Add debug information (takes precedence over --verbose).
```

## Example

```
$ shellcheck-gha .
=== Results: 2 file(s) have findings ===
Scanned 5 files (16 shell scripts)
[INFO] In bad.yaml:
    Message: Double quote to prevent globbing and word splitting.
    More information: https://www.shellcheck.net/wiki/SC2086
    Code:
        test $USE_GITIGNORE == true
             ^^^^^^^^^^^^^^^
[INFO] In tests/sample_workflows/with-findings.yaml:
    Message: Double quote to prevent globbing and word splitting.
    More information: https://www.shellcheck.net/wiki/SC2086
    Code:
        echo $BAD_JOB1
             ^^^^^^^^^^
[INFO] In tests/sample_workflows/with-findings.yaml:
    Message: Double quote to prevent globbing and word splitting.
    More information: https://www.shellcheck.net/wiki/SC2086
    Code:
        echo $BAD_JOB1
             ^^^^^^^^^^
```

## Goals

- Only check *nix related shells (sh, bash, ksh)
- Provide useful logs that allow the users to quickly find the problematic 
  code in their workflow.

## Non-Goals

- Differential checking (base vs head commit)
- Logical understanding of GitHub workflows, such as (but not limited to):
  - Handling `defaults.run.shell`
  - Support for string interpolation (`${{ ... }}`)
- Tracking down exact locations of the findings (line numbers, columns)

[ShellCheck]: https://github.com/koalaman/shellcheck
[poetry]: https://pypi.org/project/poetry/
