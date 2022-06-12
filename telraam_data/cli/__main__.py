from datetime import date, datetime
from telraam_data.query import _response_is_healthy, TELRAAM_API_URL, ENVVAR_TELRAAM_API_TOKEN
import click
import requests
import telraam_data
import sys
from enum import Enum


class ExitCode(Enum):
    SUCCESS = 0
    SRV_ERROR = 1  # Server not reachable / client rejected / invalid server response
    CLI_ERROR = 2  # Invalid user input to command-line interface


@click.group()
def cli():
    pass


@click.command()
@click.argument('segment-id', type=str)
@click.option('-s', '--start-date',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              default=None,  # defaults to earliest data point during runtime
              help="The beginning of the desired time interval. Defaults to the first day of the"
                   "specified Telraam sensor's activity."
              )
@click.option('-e', '--end-date',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today()),
              help="The end of the desired time interval. Defaults to today."
              )
@click.option('-k', '--api-key',
              type=str,
              default=ENVVAR_TELRAAM_API_TOKEN,
              help="Your personal Telraam API token. If not set, the content of the environment variable"
                   " 'TELRAAM_API_TOKEN' is used."
              )
@click.option('-o', '--output-path',
              type=click.Path(),
              default=None,  # Path defaults to generated string during runtime
              help="The path to the file where the data shall be stored."
              )
@click.pass_context
def download(ctx, segment_id, start_date, end_date, api_key, output_path):
    """Downloads and stores Telraam data from a specified road segment.
    """
    if api_key is None:
        click.echo("An API key is required.\nAborting.")
        return ExitCode.CLI_ERROR

    if start_date is not None:
        if start_date > end_date:
            click.echo("The start date must be earlier than the end date.\nAborting.")
            return ExitCode.CLI_ERROR

    url = TELRAAM_API_URL + "/cameras/segment/" + segment_id
    headers = {'X-Api-Key': api_key}
    response = requests.request("GET", url, headers=headers, data={})

    if not _response_is_healthy(response):
        if response.status_code == 403:
            click.echo("API key was rejected by the Telraam server.\nAborting.")
        else:
            click.echo("Couldn't reach url " + url + ".\nAborting.")
        sys.exit(ExitCode.SRV_ERROR)

    if len(response.json()["camera"]) == 0:
        click.echo("No segment with id " + segment_id + " found.\nAborting.")
        sys.exit(ExitCode.SRV_ERROR)

    if start_date is None:
        dates = [datetime.strptime(cam["first_data_package"], "%Y-%m-%dT%H:%M:%S.%fZ") for cam
                 in response.json()["camera"]]
        start_date = min(dates)

    if output_path is None:
        output_path = "./telraam_data_" + segment_id
        output_path += "_from_" + start_date.strftime("%Y-%m-%d")
        output_path += "_to_" + end_date.strftime("%Y-%m-%d")
        output_path += ".csv"

    click.echo(f"Segment-id: {segment_id}")
    click.echo(f"Start: {start_date.date()}, End: {end_date.date()} ")
    click.echo(f"Output path: {output_path}")

    df = telraam_data.download_one_segment(
        segment_id=segment_id,
        start_date=start_date,
        end_date=end_date,
        out_filepath=output_path,
        api_token=api_key)

    if df is None:
        click.echo("An unexpected error happened.\nAborting.")
        sys.exit(ExitCode.SRV_ERROR)

    return ExitCode.SUCCESS


cli.add_command(download)

if __name__ == '__main__':
    cli()
