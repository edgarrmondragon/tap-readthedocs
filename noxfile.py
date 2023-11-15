"""Nox configuration."""

from __future__ import annotations

import os
import sys
from textwrap import dedent

try:
    from nox_poetry import Session, session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.
    Please install it using the following command:
    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message)) from None

package = "tap-readthedocs"
src_dir = "tap_readthedocs"
tests_dir = "tests"

python_versions = ["3.12", "3.11", "3.10", "3.9", "3.8"]
main_python_version = "3.11"
locations = src_dir, tests_dir, "noxfile.py"


@session(python=python_versions)
def tests(session: Session) -> None:
    """Execute pytest tests and compute coverage."""
    deps = ["pytest"]
    if "GITHUB_ACTIONS" in os.environ:
        deps.append("pytest-github-actions-annotate-failures")

    session.install(".")
    session.install(*deps)
    session.run("pytest", *session.posargs)
