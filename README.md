shellcheck-gha
==============

![PyPI Project Version](https://img.shields.io/pypi/v/shellcheck-gha.svg)
![Supported Python Versions](https://img.shields.io/pypi/pyversions/shellcheck-gha.svg)
![Project Python Implementations](https://img.shields.io/pypi/implementation/shellcheck-gha.svg)

This Python script extracts shell scripts from GitHub workflows
(`jobs.<job_id>.steps[*].run`) and runs them against [ShellCheck].

<!-- TOC -->
* [shellcheck-gha](#shellcheck-gha)
  * [Installation](#installation)
    * [Using GitHub Actions (recommended)](#using-github-actions-recommended)
    * [PyPI](#pypi)
    * [From Source](#from-source)
  * [Usage](#usage)
  * [Example](#example)
  * [Goals](#goals)
  * [Non-Goals](#non-goals)
<!-- TOC -->

## Installation

**Requirements:**

- Python ≥ 3.11
- [ShellCheck] ≥ 0.9.0, available on `apt`, `brew`, `cabal`, `dnf`, and `pkg`.

### Using GitHub Actions (recommended)

The `shellcheck-gha` project can be used as a GitHub Workflow step:

```yaml
on:
  push:
    paths:
      - .github/**
  pull_request:
    paths:
      - .github/**

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run ShellCheck
        uses: saleor/shellcheck-gha@v0
        # Uncomment to customize the scan directory:
        # with:
        #   scan-directory-path: .github/
```

> [!IMPORTANT]  
> By default only the `./.github` directory is scanned (recursively).
> If some GitHub Composite actions are defined outside the `.github` directory,
> consider adding steps to scan the additional directories by changing the `scan-directory-path`
> parameter.

### PyPI

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
usage: shellcheck-gha [-h] [--default-shell DEFAULT_SHELL] [--verbose] [--debug] [--skip-unknown-files | --no-skip-unknown-files] [directory]

positional arguments:
  directory

options:
  -h, --help            show this help message and exit
  --default-shell DEFAULT_SHELL
                        The default shell running in the workflow(s)
  --verbose             Show more details about the execution.
  --debug               Add debug information (takes precedence over --verbose).
  --skip-unknown-files, --no-skip-unknown-files
                        Whether to exit with an error on when parsing non-GitHub workflow or composite action YAML files. Skipping is useful when a directory
                        may be mixed with other YAML files (e.g. config files such as .github/dependabot.yaml). Unknown files are skipped by default.
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
        echo $BAD_JOB2
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
