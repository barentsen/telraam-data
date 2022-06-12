from click.testing import CliRunner
from telraam_data.cli.__main__ import download as cli_download
from telraam_data.query import ENVVAR_TELRAAM_API_TOKEN
import telraam_data.query as query
import pathlib
import sys
import shutil
import random
import pytest


@pytest.fixture()
def segment_id():
    all_segments = query.query_active_segments()
    segment_idx = random.randrange(1, len(all_segments)) - 1
    return all_segments["features"][segment_idx]["properties"]["segment_id"]


@pytest.fixture()
def nonexisting_segment_id():
    existing_segments = query.query_active_segments()
    existing_segment_ids = [segment["properties"]["segment_id"] for segment in existing_segments["features"]]
    nonexisting_id = random.randint(0, sys.maxsize)
    while nonexisting_id in existing_segment_ids:
        nonexisting_id = random.randint(0, sys.maxsize)
    return nonexisting_id


@pytest.fixture()
def valid_date(segment_id):
    from telraam_data.query import TELRAAM_API_URL
    import requests
    from datetime import datetime

    url = TELRAAM_API_URL + "/cameras/segment/" + str(segment_id)
    headers = {'X-Api-Key': ENVVAR_TELRAAM_API_TOKEN}
    response = requests.request("GET", url, headers=headers, data={})
    dates = [datetime.strptime(cam["first_data_package"], "%Y-%m-%dT%H:%M:%S.%fZ") for cam in response.json()["camera"]]
    return min(dates)


@pytest.fixture()
def output_path():
    path = pathlib.Path('./data.csv')
    path.touch(exist_ok=True)
    yield path
    path.unlink()


def test_cli_success(segment_id, valid_date, output_path):
    segment_id = str(segment_id)
    valid_date = valid_date.strftime("%Y-%m-%d")
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        segment_id,
        '--start-date', valid_date,
        '--end-date', valid_date,
        '--api-key', str(ENVVAR_TELRAAM_API_TOKEN),
        '--output-path', str(output_path)
    ])
    assert result.exit_code == 0
    assert segment_id in result.output
    assert valid_date in result.output
    assert str(output_path) in result.output
    assert "Downloading data" in result.output


def test_cli_wrong_segment_id(nonexisting_segment_id, valid_date, output_path):
    nonexisting_segment_id = str(nonexisting_segment_id)
    valid_date = valid_date.strftime("%Y-%m-%d")
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        nonexisting_segment_id,
        '--start-date', valid_date,
        '--end-date', valid_date,
        '--api-key', str(ENVVAR_TELRAAM_API_TOKEN),
        '--output-path', str(output_path)
    ])
    assert result.exit_code == 1
    assert nonexisting_segment_id in result.output
    assert "Aborting." in result.output


def test_cli_wrong_dates(segment_id, valid_date, output_path):
    segment_id = str(segment_id)
    valid_date = valid_date.strftime("%Y-%m-%d")
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        segment_id,
        '--start-date', valid_date,
        '--end-date', valid_date,
        '--api-key', str(ENVVAR_TELRAAM_API_TOKEN),
        '--output-path', str(output_path)
    ])
    assert result.exit_code == 0
    assert segment_id in result.output
    assert valid_date in result.output
    assert str(output_path) in result.output
    assert "Downloading data" in result.output
    assert False


def test_cli_wrong_api_keys(segment_id):
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        str(segment_id),
        '--api-key', "This is probably an invalid API key :)",
    ])
    assert result.exit_code == 1
    assert "API key was rejected" in result.output
    assert "Aborting." in result.output

