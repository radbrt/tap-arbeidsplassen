"""Tests standard tap features using the built-in SDK tests library."""

import datetime
from singer_sdk.testing import get_tap_test_class
from tap_arbeidsplassen.tap import Taparbeidsplassen
import responses
from responses import POST, GET
import json


SAMPLE_CONFIG = {
    "start_date": "2024-12-01",
    # TODO: Initialize minimal tap config
    "auth_token": "notavalidtoken"
}


# Run standard built-in tap tests from the SDK:
# TestTaparbeidsplassen = get_tap_test_class(
#     tap_class=Taparbeidsplassen,
#     config=SAMPLE_CONFIG,
# )

def get_initial_page_response():
    with open('tests/data/initial_page_response.json', 'r') as f:
        return json.load(f)

def get_final_page_response():
    with open('tests/data/final_page_response.json', 'r') as f:
        return json.load(f)

# TODO: Create additional tests as appropriate for your tap.

@responses.activate
def test_initial_page(capsys):

    params = {
        'size': 50,
        'updated': f'[{SAMPLE_CONFIG["start_date"]},2030-12-31T00:00:00]'
    }
    responses.add(GET, 'https://arbeidsplassen.nav.no/public-feed/api/v1/ads', json=get_initial_page_response())
    responses.add(GET, 'https://arbeidsplassen.nav.no/public-feed/api/v1/ads', json=get_final_page_response())


    tap = Taparbeidsplassen(config=SAMPLE_CONFIG)
    _ = tap.streams['ads'].sync(None)


    all_outs = capsys.readouterr()

    all_stdout = all_outs.out.strip()

    stdout_parts = all_stdout.split('\n')

    assert 'SCHEMA' in all_stdout
    assert 'RECORD' in all_stdout
    assert 'STATE' in all_stdout

    assert len(stdout_parts) == 5
    # Verify that the endpoint was hit exactly twice
    assert len(responses.calls) == 2
    assert responses.calls[0].request.params == {
        'size': '50', 
        'updated': '[2024-12-01,2030-12-31T00:00:00]'
        }
    assert responses.calls[1].request.params == {
        'size': '50', 
        'updated': '[2024-12-01,2030-12-31T00:00:00]',
        'page': '1'
    }
