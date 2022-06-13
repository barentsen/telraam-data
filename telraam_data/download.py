import datetime as dt
import pandas as pd
from tqdm.auto import tqdm
import pathlib as pl
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

    Returns
    -------
    segment_ids : list of int
        IDs of all Telraam segments.
    """
    response = query_telraam.query_active_segments(api_token)
    return [feature["properties"]["segment_id"] for feature in response["features"]]


def list_segments_by_coordinates(
        lon: float,
        lat: float,
        radius: float,
        api_token: Optional[str] = None
) -> List[int]:
    """Returns the segment IDs within `radius` kilometer from (lat, lon).
    
    Parameters
    ----------
    lon : float
        Longitude in degrees.
    lat : float
        Latitude in degrees.
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
    response = query_telraam.query_active_segments_in_radius(lon, lat, radius, api_token)
    return [feature["properties"]["segment_id"] for feature in response["features"]]


def download_segments(
        segment_id: Union[str, List[str], int, List[int]],
        start_date: dt.date = dt.datetime.now().date() - dt.timedelta(weeks=1),
        end_date: dt.date = dt.datetime.now().date(),
        out_filepath: pl.Path = None,
        api_token: Optional[str] = None
) -> pd.DataFrame:
    """Returns traffic count data for one or more segments.
    
    Parameters
    ----------
    segment_id : str, list of str
        Unique segment identifier (e.g. 1003073114).
        Use `segment_id="all"` to select all segments.
    start_date : datetime.date
        Start date of the desired data. Defaults to one week ago.
    end_date : datetime.date
        End date of the desired data. Defaults to today.
    out_filepath : pathlib.Path
        Download destination path. Defaults to None (data is not stored by default).
    api_token: str
        Your personal Telraam API token.
        Defaults to the environment variable TELRAAM_API_TOKEN.
    """
    if segment_id == 'all':  # Retrieve ALL segments?
        segment_id = query_telraam.query_active_segments(api_token)
    elif isinstance(segment_id, (str, int)):  # Ensure segment_id is iterable
        segment_id = [segment_id]

    # Load data frames segment-by-segment
    data_chunks = []
    for segid in tqdm(segment_id, desc=f"Downloading Telraam segment {segment_id}"):
        try:
            data_chunks.append(download_one_segment(segid, start_date, end_date, api_token))
        except IOError as e:
            log.error(e)

    # Merge data
    df = pd.DataFrame()
    for chunk in data_chunks:
        df.join(chunk, how='outer', rsuffix=f'_{chunk.segment_id[0]}')

    if out_filepath is not None:
        path = pl.Path(out_filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_filepath)

    return df


def download_one_segment(
        segment_id: str,
        start_date: dt.date = dt.datetime.now().date() - dt.timedelta(weeks=1),
        end_date: dt.date = dt.datetime.now().date(),
        out_filepath: pl.Path = None,
        api_token: Optional[str] = None
) -> pd.DataFrame:
    """Returns information about one segment.

    Parameters
    ----------
    segment_id : str
        Unique segment identifier (e.g. "1003073114").
    start_date : datetime.date
        Start date of the desired data. Defaults to one week ago.
    end_date : datetime.date
        End date of the desired data. Defaults to today.
    out_filepath: pathlib.Path
        Download destination path. Defaults to None (data is not stored by default).
    api_token: str
        Your personal Telraam API token.
    """
    result = query_telraam.query_one_segment(segment_id, start_date, end_date, api_token)
    if result is None:
        return None

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(result['report'])
    df.date = pd.to_datetime(df.date).dt.tz_localize(None)
    df.set_index("date", inplace=True)

    # Write file
    if out_filepath is not None:
        path = pl.Path(out_filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_filepath)

    return df
