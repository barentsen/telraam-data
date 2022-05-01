import telraam_data.query as query
import telraam_data.download as download
from .utils import get_data_keys
import datetime as dt
import random
import pytest


@pytest.fixture()
def one_segment():
    all_segments = query.query_active_segments()
    segment_idx = random.randrange(1, len(all_segments)) - 1
    return all_segments["features"][segment_idx]


def test_list_segments():
    # As of April 2020 there were more than 900 active segments.
    segments = download.list_segments()
    assert len(segments) > 900


def test_list_segments_by_coordinates():
    # As of April 2020 there are more than 30 active segments in Schaarbeek
    segments = download.list_segments_by_coordinates(lon=4.373, lat=50.867, radius=2)
    assert len(segments) > 30
    # 1003073114 should be one of them
    assert 1003073114 in segments
    # 1003063473 should not be one of them
    assert 1003063473 not in segments


def test_download_one_segment(one_segment):
    segment_id = one_segment["properties"]["segment_id"]
    segment_last_time = one_segment["properties"]["last_data_package"]

    # Query that segment for the last live day
    end_date = dt.datetime.fromisoformat(segment_last_time).date()
    start_date = end_date - dt.timedelta(days=1)
    df = download.download_one_segment(segment_id, start_date, end_date)

    required_keys = get_data_keys()
    assert len(df) > 0
    assert set(required_keys) == set(required_keys).intersection(df.columns)
    # TODO: Assert that all segment ids match segment_id
    # TODO: Assert that all dates fall into the time interval (put this test in query?)


def test_download_and_store_one_segment():
    assert False


def test_download_segments():
    assert False


def download_and_store_segments():
    assert False
