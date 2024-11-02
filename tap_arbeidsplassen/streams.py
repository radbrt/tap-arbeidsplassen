"""Stream type classes for tap-arbeidsplassen."""

from __future__ import annotations

import typing as t
from importlib import resources

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_arbeidsplassen.client import arbeidsplassenStream

class UsersStream(arbeidsplassenStream):
    """Define custom stream."""

    name = "ads"
    path = "/ads"
    primary_keys: t.ClassVar[list[str]] = ["uuid"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"  # noqa: ERA001
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property(
            "uuid",
            th.StringType,
            description="Globally unique ad identifier",
        ),
        th.Property(
            "published",
            th.StringType,
            description="Date and time when ad was published",
        ),
        th.Property(
            "updated",
            th.StringType,
            description="Date and time of last update on ad",
        ),
        th.Property("expires", th.StringType),
        th.Property("workLocations", th.ArrayType(th.ObjectType())),
        th.Property("title", th.StringType, description="Ad heading"),
        th.Property("zip", th.StringType),
    ).to_dict()


class GroupsStream(arbeidsplassenStream):
    """Define custom stream."""

    name = "groups"
    path = "/groups"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "modified"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("id", th.StringType),
        th.Property("modified", th.DateTimeType),
    ).to_dict()
