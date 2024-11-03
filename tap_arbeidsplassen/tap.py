"""arbeidsplassen tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_arbeidsplassen import streams


class Taparbeidsplassen(Tap):
    """arbeidsplassen tap class."""

    name = "tap-arbeidsplassen"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "start_date",
            th.StringType,
            required=False,
            description="The start date to query from",
            default="2021-01-01",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.arbeidsplassenStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.AdsStream(self)
        ]


if __name__ == "__main__":
    Taparbeidsplassen.cli()
