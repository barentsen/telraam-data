"""Functions to retrieve data from the Telraam API."""
import datetime

from haversine import haversine
import pandas as pd
import requests
import os
from tqdm.auto import tqdm

from . import log


TELRAAM_API_URL = "https://telraam-api.net/v1"
TELRAAM_API_TOKEN = os.environ["TELRAAM_API_TOKEN"]


def list_segments(api_token: str = TELRAAM_API_TOKEN):
    """Returns a list of all active Telraam segment IDs."""
    js = _query_active_segments(api_token)
    return list(set([segment['properties']['id'] for segment in js['features']]))


def list_segments_by_coordinates(lat, lon, radius=10, api_token: str = TELRAAM_API_TOKEN):
    """Returns the segment IDs within `radius` kilometer from (lat, lon).
    
    Parameters
    ----------
    lat : float
        Latitude in degrees.
    lon : float
        Longitude in degrees.
    radius : float
        Search radius in kilometer.

    Returns
    -------
    segment_ids : list of int
        IDs of all Telraam segments located within the search radius.
    """
    js = _query_active_segments(api_token)
    result = []
    for segment in js['features']:
        segment_lon, segment_lat = segment['geometry']['coordinates'][0][0]
        distance_km = haversine((lat, lon), (segment_lat, segment_lon))
        if distance_km < radius:
            result.append(segment['properties']['id'])
    return result


def download_segment(segment_id, time_start=None, time_end=None, fmt="per-day", api_token: str = TELRAAM_API_TOKEN):
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
        segment_id = _query_active_segments(api_token)
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
    for segid in tqdm(segment_id, desc="Downloading Telraam segments"):
        try:
            data.append(_download_one_segment(segid, time_start, time_end, fmt, api_token))
        except IOError as e:
            log.error(e)
    return pd.concat(data)


###
### Helper functions
###


def _query_active_segments(api_key):
    """Radius in km"""
    url = f"{TELRAAM_API_URL}/segments/active_minimal"
    headers = {'X-Api-Key': api_key}
    js = requests.get(url, headers=headers, data={}).json()
    return js


def _query_one_segment(segment_id, time_start, time_end, fmt, api_key):
    """Returns a `dict` for one segment."""
    url = f"{TELRAAM_API_URL}/reports/traffic"
    headers = {'X-Api-Key': api_key}
    payload = str({
        "time_start": time_start,
        "time_end": time_end,
        "level": "segments",
        "format": fmt,
        "id": segment_id
    })
    log.debug(f"Querying {url} with data: {payload}")
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code >= 400:
        raise IOError(f"Query failed: {response.status_code} {response.reason}")
    return response.json()


def _download_one_segment(segment_id, time_start, time_end, fmt, api_key):
    """Returns a `pandas.DataFrame` for one segment."""
    js = _query_one_segment(segment_id, time_start, time_end, fmt, api_key)
    n_reports = len(js['report'])
    log.debug(f"Found {n_reports} reports.")
    if n_reports == 0:
        return None
    df = pd.DataFrame.from_dict(js['report'])
    # Remove timezone info using `tz_localize(None)` to support `to_excel()`
    df.date = pd.to_datetime(df.date).dt.tz_localize(None)
    return df
