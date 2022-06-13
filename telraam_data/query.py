"""Functions to retrieve data from the Telraam API."""
import requests
import datetime as dt
from typing import Dict, Optional
from . import log
from tqdm.auto import tqdm
import os

TELRAAM_API_URL = "https://telraam-api.net/v1"
ENVVAR_TELRAAM_API_TOKEN = os.environ.get("TELRAAM_API_TOKEN")


def _response_is_healthy(response: requests.Response) -> bool:
    return response.status_code == 200


def check_response_health(response: requests.Response) -> None:
    if not _response_is_healthy(response):
        raise IOError(f"Query failed: {response.status_code} {response.reason}")


def query_active_segments(api_token: Optional[str] = ENVVAR_TELRAAM_API_TOKEN) -> Dict:
    """Returns information about all active segments.

    Parameters
    ----------
    api_token: str
        Your personal Telraam API token.

    Returns
    -------
    response_json : Dict
        A dictionary containing the database's response.
    """
    url = f"{TELRAAM_API_URL}/reports/traffic_snapshot"
    headers = {'X-Api-Key': ENVVAR_TELRAAM_API_TOKEN if api_token is None else api_token}
    payload = str({
        "time": "live",
        "contents": "minimal",
        "area": "full"
    })
    log.debug(f"Querying all active segments from {url}.")
    response = requests.post(url, headers=headers, data=payload)
    check_response_health(response)
    return response.json()


def query_active_segments_in_radius(
        lon: float,
        lat: float,
        radius: float = 10,
        api_token: Optional[str] = None
) -> Dict:
    """Returns information about all active segments in a circular region.

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

    Returns
    -------
    response_json : Dict
        A dictionary containing the database's response.
    """
    url = f"{TELRAAM_API_URL}/reports/traffic_snapshot"
    headers = {'X-Api-Key': ENVVAR_TELRAAM_API_TOKEN if api_token is None else api_token}
    payload = str({
        "time": "live",
        "contents": "minimal",
        "area": f"{lon},{lat},{radius}"
    })
    log.debug(f"Querying all active segments in a {radius}km radius at latitude {lat}° and longitude {lon}°"
              f"from {url}.")
    response = requests.post(url, headers=headers, data=payload)
    check_response_health(response)
    return response.json()


def query_one_segment(
        segment_id: str,
        start_date: dt.date,
        end_date: dt.date,
        api_token: Optional[str] = None
) -> Dict:
    """Returns traffic information for one segment.

    Parameters
    ----------
    segment_id : str
        Unique segment identifier (e.g. "1003073114").
    start_date : datetime.date
        Start date of the desired data.
    end_date : datetime.date
        End date of the desired data.
    api_token: str
        Your personal Telraam API token.
        Defaults to the environment variable TELRAAM_API_TOKEN.

    Returns
    -------
    response_json : Dict
        A dictionary containing the database's response.
    """
    url = f"{TELRAAM_API_URL}/reports/traffic"
    headers = {'X-Api-Key': ENVVAR_TELRAAM_API_TOKEN if api_token is None else api_token}

    # Query can be 92 days long max
    # Get time-intervals that shall be downloaded one by one
    time_step = dt.timedelta(days=90)
    dates = [start_date]
    while dates[-1] < end_date:
        dates.append(dates[-1] + time_step)

    # Query all data intervals
    responses = []
    for i in tqdm(range(len(dates) - 1), desc=f"Downloading data from {start_date} to {end_date}"):
        start_date = dates[i]
        end_date = dates[i + 1]
        payload = str({
            "time_start": start_date.strftime("%Y-%m-%d 00:00:00Z"),
            "time_end": end_date.strftime("%Y-%m-%d 23:59:59Z"),
            "level": "segments",
            "format": "per-hour",
            "id": segment_id
        })
        log.debug(f"Querying {url} with data: {payload}")
        response = requests.post(url, headers=headers, data=payload)
        if _response_is_healthy(response):
            responses.append(response)
        else:
            log.info(f"No data found for time interval {start_date} to {end_date}")

    if len(responses) == 0:
        log.info(f"Data could not be queried.")
        return None

    # Assemble data intervals
    json = {'status_code': responses[0].json()['status_code'], 'message': responses[0].json()['message'], 'report': []}
    for response in responses:
        json['report'].extend(response.json()['report'])

    return json
