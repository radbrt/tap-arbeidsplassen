"""REST client handling, including arbeidsplassenStream base class."""

from __future__ import annotations

import typing as t
from importlib import resources

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, BasePageNumberPaginator  # noqa: TCH002
from singer_sdk.streams import RESTStream
from singer_sdk.helpers._typing import TypeConformanceLevel
import re

import spacy


from singer_sdk.pagination import BaseOffsetPaginator

class MyPaginator(BasePageNumberPaginator):
    def has_more(self, response):
        data = response.json()
        return not data.get("last", True)


if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context


# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = resources.files(__package__) / "schemas"


class arbeidsplassenStream(RESTStream):
    """arbeidsplassen stream class."""

    # Update this value if necessary or override `parse_response`.
    records_jsonpath = "$.content[*]"
    rest_method = "GET"
    PAGE_SIZE = 1
    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.ROOT_ONLY


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_dir = resources.files('tap_arbeidsplassen') / 'nb_small'
        self.nlp = spacy.load(model_dir)

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://arbeidsplassen.nav.no/public-feed/api/v1/"

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("auth_token", ""),
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("auth_token")  # noqa: ERA001
        return headers


    def get_new_paginator(self):
        return BaseOffsetPaginator(start_value=0, page_size=self.PAGE_SIZE)

    def get_url_params(self, context, next_page_token):

        start_date = self.get_starting_replication_key_value(context) or self.config.get("start_date", "2024-12-03")
        params = {
            'size': 50,
            'updated': f'[{start_date}, 2030-12-31T00:00:00]' # self.config.get("start_date", "2021-01-01")
            }

        # Next page token is an offset
        if next_page_token:
            params["page"] = next_page_token

        self.logger.info(f"params: {params}")
        return params


    # def get_url_params(
    #     self,
    #     context: Context | None,  # noqa: ARG002
    #     next_page_token: t.Any | None,  # noqa: ANN401
    # ) -> dict[str, t.Any]:
    #     """Return a dictionary of values to be used in URL parameterization.

    #     Args:
    #         context: The stream context.
    #         next_page_token: The next page index or value.

    #     Returns:
    #         A dictionary of URL query parameters.
    #     """
    #     params: dict = {}
    #     # params["updated"] = self.config.get("start_date", "2021-01-01")
    #     # if next_page_token:
    #     #     params["page"] = next_page_token
    #     # if self.replication_key:
    #     #     params["sort"] = "asc"
    #     #     params["order_by"] = self.replication_key
    #     return params


    def prepare_request_payload(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002, ANN401
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        starting_date = self.get_starting_replication_key_value(
            context
        ) or self.config.get("start_date")

        return None

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(
        self,
        row: dict,
        context: Context | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        txt = row["description"]
        new_txt = ""
        doc = self.nlp(txt)
        # Replace PER entities with N.N.
        # Reverse order to avoid changing indices
        for ent in reversed(doc.ents):
            if ent.label_ == "PER":
                new_txt = txt[:ent.start_char] + "N.N." + txt[ent.end_char:]

        # Replace email addresses with N.N.
        new_txt = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'N.N.', new_txt)

        # replace strings of numbers longer than 3 with N.N.
        new_txt = re.sub(r'\d{4,}', 'X', new_txt)

        if not new_txt:
            row["description"] = txt
        else:
            row["description"] = new_txt

        return row
