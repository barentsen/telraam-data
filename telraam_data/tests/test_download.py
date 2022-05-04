import telraam_data.query as query
import telraam_data.download as download
from .utils import get_data_keys
import datetime as dt
import shutil
import pandas as pd
import pathlib as pl
import random
import pytest


@pytest.fixture()
def one_segment():
    all_segments = query.query_active_segments()
    segment_idx = random.randrange(1, len(all_segments)) - 1
    return all_segments["features"][segment_idx]


@pytest.fixture()
def tmp_path():
    path = pl.Path('./tmp/data.csv')
    yield path
    shutil.rmtree('./tmp/')


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


def test_download_one_segment(one_segment, tmp_path):
    segment_id = one_segment["properties"]["segment_id"]
    segment_last_time = one_segment["properties"]["last_data_package"]

    # Query that segment for the last live day
    end_date = dt.datetime.fromisoformat(segment_last_time).date()
    start_date = end_date - dt.timedelta(days=1)
    df = download.download_one_segment(
        segment_id=segment_id,
        start_date=start_date,
        end_date=end_date,
        out_filepath=tmp_path)

    required_keys = get_data_keys()
    required_keys.remove('date')  # 'date' has become the index

    # 1. Check returned data
    assert len(df) > 0
    assert df.index.name == 'date'
    assert (df.index >= str(start_date)).all()
    assert (df.index <= str(end_date + dt.timedelta(days=1))).all()
    assert set(required_keys) == set(required_keys).intersection(df.columns)
    assert (df['segment_id'] == segment_id).all()

    # 2. Check stored data
    df_local = pd.read_csv(tmp_path, parse_dates=["date"], index_col="date")
    from ast import literal_eval
    df_local.car_speed_hist_0to70plus = df_local.car_speed_hist_0to70plus.apply(literal_eval)
    df_local.car_speed_hist_0to120plus = df_local.car_speed_hist_0to120plus.apply(literal_eval)
    assert (df_local == df).all().all()
