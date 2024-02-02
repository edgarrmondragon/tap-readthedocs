"""Stream type classes for tap-readthedocs."""
from __future__ import annotations

import logging
import typing as t

from singer_sdk import typing as th
from toolz.dicttoolz import update_in

from tap_readthedocs.client import ReadTheDocsStream

logger = logging.getLogger(__name__)


class Projects(ReadTheDocsStream):
    """Projects stream."""

    name = "projects"
    path = "/api/v3/projects/"
    primary_keys = ("id",)

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("slug", th.StringType),
        th.Property("created", th.DateTimeType),
        th.Property("modified", th.DateTimeType),
        th.Property(
            "language",
            th.ObjectType(
                th.Property("code", th.StringType),
                th.Property("name", th.StringType),
            ),
        ),
        th.Property(
            "programming_language",
            th.ObjectType(
                th.Property("url", th.StringType),
                th.Property("type", th.StringType),
            ),
        ),
        th.Property(
            "repository",
            th.ObjectType(
                th.Property("url", th.StringType),
                th.Property("type", th.StringType),
            ),
        ),
        th.Property("default_version", th.StringType),
        th.Property("default_branch", th.StringType),
        th.Property("subproject_of", th.IntegerType),
        th.Property("translation_of", th.IntegerType),
        th.Property("urls", th.ObjectType()),
        th.Property("tags", th.ArrayType(th.StringType)),
        th.Property(
            "users",
            th.ArrayType(
                th.ObjectType(
                    th.Property("username", th.StringType),
                ),
            ),
        ),
        th.Property("active_versions", th.ObjectType()),
        th.Property("homepage", th.StringType),
    ).to_dict()

    def get_child_context(
        self,
        record: dict[str, t.Any],
        context: dict[str, t.Any] | None,  # noqa: ARG002
    ) -> dict[str, t.Any] | None:
        """Get child context for a project.

        Args:
            record: Project record.
            context: Stream sync context.

        Returns:
            Dictionary of a project context.
        """
        return {"project_slug": record["slug"]}


class Versions(ReadTheDocsStream):
    """Versions stream."""

    name = "versions"
    path = "/api/v3/projects/{project_slug}/versions"
    primary_keys = ("id",)
    parent_stream_type = Projects

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("project_slug", th.StringType),
        th.Property("slug", th.StringType),
        th.Property("verbose_name", th.StringType),
        th.Property("identifier", th.StringType),
        th.Property("ref", th.StringType),
        th.Property("built", th.BooleanType),
        th.Property("active", th.BooleanType),
        th.Property("hidden", th.BooleanType),
        th.Property("type", th.StringType),
        th.Property("last_build", th.IntegerType),
        th.Property("downloads", th.ObjectType()),
        th.Property("urls", th.ObjectType()),
    ).to_dict()


class Builds(ReadTheDocsStream):
    """Builds stream."""

    name = "builds"
    path = "/api/v3/projects/{project_slug}/builds"
    primary_keys = ("id",)
    parent_stream_type = Projects

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("project_slug", th.StringType),
        th.Property("version", th.StringType),
        th.Property("project", th.StringType),
        th.Property("created", th.DateTimeType),
        th.Property("finished", th.DateTimeType),
        th.Property("duration", th.IntegerType),
        th.Property(
            "state",
            th.ObjectType(
                th.Property("code", th.StringType),
                th.Property("name", th.StringType),
            ),
        ),
        th.Property("success", th.BooleanType),
        th.Property("error", th.StringType),
        th.Property("commit", th.StringType),
        th.Property("urls", th.ObjectType()),
        th.Property(
            "config",
            th.ObjectType(
                th.Property("version", th.StringType),
                th.Property("formats", th.ArrayType(th.StringType)),
                # TODO(edgarrmondragon): add other configs here (sphinx, etc.)
                # https://github.com/edgarrmondragon/tap-readthedocs/issues/227
                th.Property(
                    "python",
                    th.ObjectType(
                        th.Property("version", th.StringType),
                        th.Property(
                            "install",
                            th.ArrayType(
                                th.ObjectType(
                                    th.Property("requirements", th.StringType),
                                    th.Property("method", th.StringType),
                                    th.Property("path", th.StringType),
                                    th.Property(
                                        "extra_requirements",
                                        th.ArrayType(th.StringType),
                                    ),
                                ),
                            ),
                        ),
                        th.Property("system_packages", th.BooleanType),
                    ),
                ),
            ),
        ),
    ).to_dict()

    def post_process(
        self,
        row: dict[str, t.Any],
        context: dict[str, t.Any] | None = None,  # noqa: ARG002
    ) -> dict[str, t.Any] | None:
        """Modify build record.

        Args:
            row: Build record.
            context: Stream sync context.

        Returns:
            Modified record dictionary.
        """
        if row["config"]:
            row = update_in(row, ["config", "python", "version"], str, "")
        return row


class Subprojects(ReadTheDocsStream):
    """Subprojects stream."""

    name = "subprojects"
    path = "/api/v3/projects/{project_slug}/subprojects"
    primary_keys = ("id",)
    parent_stream_type = Projects

    # TODO(edgarrmondragon): get the complete schema
    # https://github.com/edgarrmondragon/tap-readthedocs/issues/2
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
    ).to_dict()


class Translations(ReadTheDocsStream):
    """Translations stream."""

    name = "translations"
    path = "/api/v3/projects/{project_slug}/translations"
    primary_keys = ("id",)
    parent_stream_type = Projects

    # TODO(edgarrmondragon): get the complete schema
    # https://github.com/edgarrmondragon/tap-readthedocs/issues/2
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
    ).to_dict()


class Redirects(ReadTheDocsStream):
    """Redirects stream."""

    name = "redirects"
    path = "/api/v3/projects/{project_slug}/redirects"
    primary_keys = ("id",)
    parent_stream_type = Projects

    # TODO(edgarrmondragon): get the complete schema
    # https://github.com/edgarrmondragon/tap-readthedocs/issues/2
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        # TODO(edgarrmondragon): Inform max length of 255
        # https://github.com/edgarrmondragon/tap-readthedocs/issues/295
        th.Property("redirect_type", th.StringType),
        # TODO(edgarrmondragon): Inform max length of 255
        # https://github.com/edgarrmondragon/tap-readthedocs/issues/295
        th.Property(
            "from_url",
            th.StringType,
            description="Absolute path, excluding the domain",
            examples=["/docs/", "/install.html"],
        ),
        # TODO(edgarrmondragon): Inform max length of 255
        # https://github.com/edgarrmondragon/tap-readthedocs/issues/295
        th.Property(
            "to_url",
            th.StringType,
            description="Absolute or relative URL",
            examples=["/tutorial/install.html"],
        ),
        th.Property(
            "force",
            th.BooleanType,
            description="Apply the redirect even if the page exists",
        ),
        # TODO(edgarrmondragon): Inform "small" integer
        # https://github.com/edgarrmondragon/tap-readthedocs/issues/295
        th.Property(
            "http_status",
            th.IntegerType,
            description="HTTP status code for the redirect",
        ),
        th.Property("enabled", th.BooleanType),
        # TODO(edgarrmondragon): Inform max length of 255
        # https://github.com/edgarrmondragon/tap-readthedocs/issues/295
        th.Property("description", th.StringType),
        # TODO(edgarrmondragon): Inform positive integer
        # https://github.com/edgarrmondragon/tap-readthedocs/issues/295
        th.Property(
            "position",
            th.IntegerType,
            description="Order of execution of the redirect",
        ),
        th.Property("create_dt", th.DateTimeType),
        th.Property("update_dt", th.DateTimeType),
    ).to_dict()


class Organizations(ReadTheDocsStream):
    """Organizations stream."""

    name = "organizations"
    path = "/api/v3/organizations/"
    primary_keys = ("slug",)

    schema = th.PropertiesList(
        th.Property("slug", th.StringType),
        th.Property("name", th.StringType),
        th.Property("url", th.StringType),
        th.Property("email", th.StringType),
        th.Property("description", th.StringType),
        th.Property("created", th.DateTimeType),
        th.Property("modified", th.DateTimeType),
        th.Property("disabled", th.BooleanType),
        th.Property(
            "owners",
            th.ArrayType(
                th.ObjectType(
                    th.Property("username", th.StringType),
                ),
            ),
        ),
    ).to_dict()
