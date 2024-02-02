<div align="center">

# tap-readthedocs

<div>
  <a href="https://results.pre-commit.ci/latest/github/edgarrmondragon/tap-readthedocs/main">
    <img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/edgarrmondragon/tap-readthedocs/main.svg"/>
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img alt="Ruff" style="max-width:100%;" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json">
  </a>
  <a href="https://github.com/pypa/hatch">
    <img alt="Hatch project" src="https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg"/>
  </a>
  <a href="https://github.com/edgarrmondragon/tap-readthedocs/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/edgarrmondragon/tap-readthedocs"/>
  </a>
  <a href="https://github.com/edgarrmondragon/tap-readthedocs/">
    <img alt="PyPI" src="https://img.shields.io/pypi/pyversions/tap-readthedocs"/>
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
| include_business_streams | False | False | Whether to include streams available only to ReadTheDocs for Business accounts |

A full list of supported settings and capabilities is available by running: `tap-readthedocs --about`

## Installation

```bash
pipx install tap-readthedocs
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
pipx install hatch
```

### Create and Run Tests

Run integration tests:

```bash
hatch run tests:integration
```

You can also test the `tap-readthedocs` CLI interface directly:

```bash
hatch run sync:console -- --about --format=json
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Go ahead and [install Meltano](https://docs.meltano.com/getting-started/installation/) if you haven't already.

1. Install all plugins

   ```bash
   meltano install
   ```

2. Check that the extractor is working properly

   ```bash
   meltano invoke tap-readthedocs --version
   ```

3. Execute an ELT pipeline

   ```bash
   meltano run tap-readthedocs target-jsonl
   ```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
