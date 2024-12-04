"""Stream type classes for tap-arbeidsplassen."""

from __future__ import annotations

import typing as t
from importlib import resources

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_arbeidsplassen.client import arbeidsplassenStream
from singer_sdk.helpers._typing import TypeConformanceLevel

class AdsStream(arbeidsplassenStream):
    """Define custom stream."""

    name = "ads"
    path = "ads"
    primary_keys: t.ClassVar[list[str]] = ["uuid"]
    replication_key = "updated"
    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY

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
        th.Property("expires", th.StringType, required=False),
        th.Property("workLocations", th.ArrayType(th.ObjectType()), required=False),
        th.Property("title", th.StringType, description="Ad heading", required=False),
        th.Property("description", th.StringType, description="Ad text", required=False),
        th.Property("sourceurl", th.StringType, description="Ad source URL", required=False),
        th.Property("source", th.StringType, description="Ad source", required=False),
        th.Property("applicationUrl", th.StringType, description="Ad application URL", required=False),
        th.Property("applicationDue", th.StringType, description="Ad application due date", required=False),
        th.Property("occupationCategories", th.ArrayType(th.ObjectType()), description="Ad occupation categories", required=False),
        th.Property("jobtitle", th.StringType, description="Ad job title", required=False),
        th.Property("link", th.StringType, description="Ad link", required=False),
        th.Property("employer", th.ObjectType(), description="Employer information", required=False),
        th.Property("engagementtype", th.StringType, description="Ad engagement type", required=False),
        th.Property("extent", th.StringType, description="Work extent", required=False),
        th.Property("starttime", th.StringType, description="Job start date", required=False),
        th.Property("positioncount", th.StringType, description="Number of positions", required=False),
        th.Property("sector", th.StringType, description="Employment sector", required=False),
    ).to_dict()

