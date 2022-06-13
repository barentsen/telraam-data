from click.testing import CliRunner
from telraam_data.cli.__main__ import download as cli_download
from telraam_data.query import ENVVAR_TELRAAM_API_TOKEN, TELRAAM_API_URL
import telraam_data.query as query
import datetime as dt
import requests
import pathlib
import sys
import random
import pytest


@pytest.fixture()
def valid_segment_id():
    all_segments = query.query_active_segments()
    segment_idx = random.randrange(1, len(all_segments)) - 1
    return all_segments["features"][segment_idx]["properties"]["segment_id"]


@pytest.fixture()
def invalid_segment_id():
    existing_segments = query.query_active_segments()
    existing_segment_ids = [segment["properties"]["segment_id"] for segment in existing_segments["features"]]
    some_id = random.randint(0, sys.maxsize)
    while some_id in existing_segment_ids:
        some_id = random.randint(0, sys.maxsize)
    return some_id


@pytest.fixture()
def valid_date(valid_segment_id):
    url = TELRAAM_API_URL + "/cameras/segment/" + str(valid_segment_id)
    headers = {'X-Api-Key': ENVVAR_TELRAAM_API_TOKEN}
    response = requests.request("GET", url, headers=headers, data={})
    dates = [dt.datetime.strptime(cam["first_data_package"], "%Y-%m-%dT%H:%M:%S.%fZ") for cam
             in response.json()["camera"]]
    return min(dates)


@pytest.fixture()
def output_path():
    path = pathlib.Path('./data.csv')
    path.touch(exist_ok=True)
    yield path
    path.unlink()


def test_cli_success(valid_segment_id, valid_date, output_path):
    valid_segment_id = str(valid_segment_id)
    start_date = valid_date.strftime("%Y-%m-%d")
    end_date = (valid_date + dt.timedelta(days=1)).strftime("%Y-%m-%d")
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        valid_segment_id,
        '--start-date', start_date,
        '--end-date', end_date,
        '--api-key', str(ENVVAR_TELRAAM_API_TOKEN),
        '--output-path', str(output_path)
    ])
    assert result.exit_code == 0
    assert valid_segment_id in result.output
    assert start_date in result.output
    assert end_date in result.output
    assert str(output_path) in result.output
    assert "Downloading data" in result.output


def test_cli_invalid_segment_id(invalid_segment_id, valid_date, output_path):
    invalid_segment_id = str(invalid_segment_id)
    valid_date = valid_date.strftime("%Y-%m-%d")
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        invalid_segment_id,
        '--start-date', valid_date,
        '--end-date', valid_date,
        '--api-key', str(ENVVAR_TELRAAM_API_TOKEN),
        '--output-path', str(output_path)
    ])
    assert result.exit_code == 1
    assert invalid_segment_id in result.output
    assert "Aborting." in result.output


def test_cli_invalid_dates(valid_segment_id, valid_date, output_path):
    valid_segment_id = str(valid_segment_id)
    start_date = (valid_date + dt.timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = valid_date.strftime("%Y-%m-%d")
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        valid_segment_id,
        '--start-date', start_date,
        '--end-date', end_date,
        '--api-key', str(ENVVAR_TELRAAM_API_TOKEN),
        '--output-path', str(output_path)
    ])
    assert result.exit_code == 1
    assert "start date must be earlier than the end date" in result.output


def test_cli_invalid_api_key(valid_segment_id):
    runner = CliRunner()
    result = runner.invoke(cli_download, [
        str(valid_segment_id),
        '--api-key', "This is probably an invalid API key :)",
    ])
    assert result.exit_code == 1
    assert "API key was rejected" in result.output
    assert "Aborting." in result.output

