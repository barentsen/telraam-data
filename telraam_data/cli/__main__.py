from datetime import date, datetime
from telraam_data.query import _response_is_healthy, TELRAAM_API_URL, ENVVAR_TELRAAM_API_TOKEN
import click
import requests


@click.group()
def cli():
    pass


@click.command()
@click.argument('segment-id', type=str)
@click.option('--start-date',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              default=None,  # defaults to earliest data point during runtime
              )
@click.option('--end-date',
              type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today())
              )
@click.option('--api-key',
              type=str,
              default=ENVVAR_TELRAAM_API_TOKEN)
def download(segment_id, start_date, end_date, api_key):
    """ TODO : Command Documentation
    """
    if api_key is None:
        click.echo("An API key is required.")
        click.echo("Aborting.")
        return

    url = TELRAAM_API_URL + "/cameras/segment/" + segment_id
    headers = {'X-Api-Key': ENVVAR_TELRAAM_API_TOKEN}
    response = requests.request("GET", url, headers=headers, data={})

    if not _response_is_healthy(response):
        click.echo("Couldn't reach url " + url + ".")
        click.echo("Aborting.")
        return

    if len(response.json()["camera"]) == 0:
        click.echo("No segment with id " + segment_id + " found.")
        click.echo("Aborting.")
        return

    if start_date is None:
        start_date = end_date
        dates = [datetime.strptime(cam["first_data_package"], "%Y-%m-%dT%H:%M:%S.%fZ") for cam in response.json()["camera"]]
        start_date = min(dates)

        #for camera in response.json()["camera"]:
        #    first_data_package_date = datetime.strptime(camera["first_data_package"], "format")
        #    if first_data_package_date < start_date:
        #        start_date = first_data_package_date

    click.echo(f"Start: {start_date}, End: {end_date} ")
    click.echo(f"Segment-id: {segment_id}, api-key: {api_key} ")


cli.add_command(download)

if __name__ == '__main__':
    cli()
