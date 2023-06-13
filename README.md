<div align="center">

# tap-readthedocs

<div>
  <a href="https://results.pre-commit.ci/latest/github/edgarrmondragon/tap-readthedocs/main">
    <img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/edgarrmondragon/tap-readthedocs/main.svg"/>
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img alt="Ruff" style="max-width:100%;" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json">
  </a>
  <a href="https://github.com/wntrblm/nox">
    <img alt="Nox" src="https://img.shields.io/badge/%F0%9F%A6%8A-Nox-D85E00.svg"/>
  </a>
  <a href="https://github.com/edgarrmondragon/tap-readthedocs/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/edgarrmondragon/tap-readthedocs"/>
  </a>
  <a href="https://github.com/edgarrmondragon/tap-readthedocs/">
    <img alt="License" src="https://img.shields.io/pypi/pyversions/tap-readthedocs"/>
  </a>
</div>

Singer Tap for [**Read the Docs**](https://docs.readthedocs.io). Built with the [Meltano Singer SDK](https://sdk.meltano.com).

</div>

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`

## Settings

| Setting| Required | Default | Description |
|:-------|:--------:|:-------:|:------------|
| token  | True     | None    |             |

A full list of supported settings and capabilities is available by running: `tap-readthedocs --about`

## Installation

```bash
pipx install git+https://github.com/edgarrmondragon/tap-readthedocs.git
```

### Source Authentication and Authorization

Generate a token: https://readthedocs.org/accounts/tokens/.

## Usage

You can easily run `tap-readthedocs` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-readthedocs --version
tap-readthedocs --help
tap-readthedocs --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` folder and then run:

```bash
poetry run pytest
```

You can also test the `tap-readthedocs` CLI interface directly using `poetry run`:

```bash
poetry run tap-readthedocs --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-readthedocs
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-readthedocs --version
# OR run a test `elt` pipeline:
meltano elt tap-readthedocs target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
