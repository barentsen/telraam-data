import datetime
import pandas
from haversine import haversine
import pandas as pd
import os
from tqdm.auto import tqdm
from typing import List, Union, Optional
from . import log
import telraam_data.query as query_telraam


def list_segments(api_token: Optional[str] = None) -> List[int]:
    """Returns a list of all active Telraam segment IDs.

    Parameters
    ----------
    api_token: str
        Your personal Telraam API token.
        Defaults to the environment variable TELRAAM_API_TOKEN.
    """
    js = query_telraam.query_active_segments(api_token)
    return list(set([segment['properties']['id'] for segment in js['features']]))


def list_segments_by_coordinates(
        lat: float,
        lon: float,
        radius: float = 10,
        api_token: Optional[str] = None
) -> List[int]:
    """Returns the segment IDs within `radius` kilometer from (lat, lon).
    
    Parameters
    ----------
    lat : float
        Latitude in degrees.
    lon : float
        Longitude in degrees.
    radius : float
        Search radius in kilometer.
    api_token: str
        Your personal Telraam API token.
        Defaults to the environment variable TELRAAM_API_TOKEN.

    Returns
    -------
    segment_ids : list of int
        IDs of all Telraam segments located within the search radius.
    """
    js = query_telraam.query_active_segments(api_token)
    result = []
    for segment in js['features']:
        segment_lon, segment_lat = segment['geometry']['coordinates'][0][0]
        distance_km = haversine((lat, lon), (segment_lat, segment_lon))
        if distance_km < radius:
            result.append(segment['properties']['id'])
    return result


def download_segment(
        segment_id: Union[str, List[str], int, List[int]],
        time_start: str = None,
        time_end: str = None,
        api_token: Optional[str] = None
) -> pandas.DataFrame:
    """Returns traffic count data for one or more segments.
    
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
    api_token: str
        Your personal Telraam API token.
        Defaults to the environment variable TELRAAM_API_TOKEN.
    """
    if segment_id == 'all':  # Retrieve ALL segments?
        segment_id = query_telraam.query_active_segments(api_token)
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
            data.append(_download_one_segment(segid, time_start, time_end, api_token))
        except IOError as e:
            log.error(e)
    return pd.concat(data)


def _download_one_segment(
        segment_id: str,
        time_start: str,
        time_end: str,
        api_token: Optional[str] = None
) -> pandas.DataFrame:
    """Returns information about one segment.

    Parameters
    ----------
    segment_id : str
        Unique segment identifier (e.g. "1003073114").
    time_start : str
        Start time in "YYYY-MM-DD HH:MM:SSZ" format (e.g "2020-01-01 00:00:00Z").
    time_end : str
        End time in the same format as `time_start`.
    api_token: str
        Your personal Telraam API token.
    """
    js = query_telraam.query_one_segment(segment_id, time_start, time_end, api_token)
    n_reports = len(js['report'])
    log.debug(f"Found {n_reports} reports.")
    if n_reports == 0:
        return None
    df = pd.DataFrame.from_dict(js['report'])
    # Remove timezone info using `tz_localize(None)` to support `to_excel()`
    df.date = pd.to_datetime(df.date).dt.tz_localize(None)
    return df
