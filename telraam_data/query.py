"""Functions to retrieve data from the Telraam API."""
import requests
from typing import Dict, Optional
from . import log
import os

TELRAAM_API_URL = "https://telraam-api.net/v1"
ENVVAR_TELRAAM_API_TOKEN = os.environ.get("TELRAAM_API_TOKEN")


def check_response_health(response: requests.Response) -> None:
    if response.status_code >= 400:
        raise IOError(f"Query failed: {response.status_code} {response.reason}")


def query_active_segments(api_token: Optional[str] = ENVVAR_TELRAAM_API_TOKEN) -> Dict:
    """Returns information about all active segments.

    Parameters
    ----------
    api_token: str
        Your personal Telraam API token.
    """
    url = f"{TELRAAM_API_URL}/reports/traffic_snapshot"
    headers = {'X-Api-Key': api_token}
    payload = str({
        "time": "live",
        "contents": "minimal",
        "area": "full"
    })
    log.debug(f"Querying all active segments from {url}.")
    response = requests.post(url, headers=headers, data=payload)
    check_response_health(response)
    return response.json()


def query_one_segment(
        segment_id: str,
        time_start: str,
        time_end: str,
        api_token: Optional[str] = ENVVAR_TELRAAM_API_TOKEN
) -> Dict:
    """Returns traffic information for one segment.

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
    url = f"{TELRAAM_API_URL}/reports/traffic"
    headers = {'X-Api-Key': api_token}
    payload = str({
        "time_start": time_start,
        "time_end": time_end,
        "level": "segments",
        "format": "per-hour",
        "id": segment_id
    })
    log.debug(f"Querying {url} with data: {payload}")
    response = requests.post(url, headers=headers, data=payload)
    check_response_health(response)
    return response.json()
