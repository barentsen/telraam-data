"""Functions to retrieve data from the Telraam API."""
import datetime

import pandas as pd
import requests
from tqdm.auto import tqdm

from . import log


TELRAAM_API_URL = "https://telraam-api.net/v0"


def download_segment(segment_id, time_start=None, time_end=None, fmt="per-day"):
    """Returns a `pandas.DataFrame` with counts for one or more segments.
    
    Parameters
    ----------
    segment_id : str, list of str
        Unique segment identifier (e.g. "1003073114").
        Use `segment_id="all"` to select all segments.
    time_start : str
        Start time in "YYYY-MM-DD HH:MM:SSZ" format (e.g "2020-01-01 00:00:00Z").
        Defaults to midnight one week ago.
    time_end : str
        End time in the same format as `time_start`.
        Defaults to mignight tonight.
    fmt : "per-hour" or "per-day"
        Should counts be reported per hour or per day?
    """
    if segment_id == 'all':  # Retrieve ALL segments?
        segment_id = _query_segment_ids()
    elif isinstance(segment_id, (str, int)):  # Ensure segment_id is iterable
        segment_id = [segment_id]

    # Set defaults for time_start and time_end
    if time_start is None:  # Defaults to one week ago
        time_start = (datetime.datetime.now() - datetime.timedelta(weeks=1)) \
                        .strftime("%Y-%m-%d 00:00:00Z")
    if time_end is None:  # Defaults to midnight tonight
        time_end = datetime.datetime.now().strftime("%Y-%m-%d 23:59:59Z")

    # Load data frames segment-by-segment
    data = []
    for segid in tqdm(segment_id, desc="Querying segments"):
        try:
            data.append(_download_one_segment(segid, time_start, time_end, fmt))
        except IOError as e:
            log.error(e)
    return pd.concat(data)


###
### Helper functions
###

def _query_segment_ids():
    """Returns the set of all TelRaam `segment_id` values."""
    url = f"{TELRAAM_API_URL}/cameras"
    js = requests.get(url).json()
    return list(set([cam['segment_id'] for cam in js['cameras']]))


def _query_one_segment(segment_id, time_start, time_end, fmt):
    """Returns a `dict` for one segment."""
    url = f"{TELRAAM_API_URL}/reports/{segment_id}"
    headers = {'Content-Type': 'application/json'}
    json_post = {
        "time_start": time_start,
        "time_end": time_end,
        "level": "segments",
        "format": fmt
    }
    log.debug(f"Querying {url} with data: {json_post}")
    response = requests.post(url, headers=headers, json=json_post)
    if response.status_code >= 400:
        raise IOError(f"Query failed: {response.status_code} {response.reason}")
    return response.json()


def _download_one_segment(segment_id, time_start, time_end, fmt):
    """Returns a `pandas.DataFrame` for one segment."""
    js = _query_one_segment(segment_id, time_start, time_end, fmt)
    n_reports = len(js['report'])
    log.debug(f"Found {n_reports} reports.")
    if n_reports == 0:
        return None
    df = pd.DataFrame.from_dict(js['report'])
    # Remove timezone info using `tz_localize(None)` to support `to_excel()`
    df.date = pd.to_datetime(df.date).dt.tz_localize(None)
    return df
