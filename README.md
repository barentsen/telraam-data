# telraam-data

**A friendly Python package to download traffic count data from Telraam.net.**

The `telraam_data` package enables you to retrieve traffic count data from the
[Telraam Project](https://telraam.net) API into `pandas.DataFrame` objects.


## Examples

### Command-Line Interface
Displaying help and usage
```bash
> telraam-data-manager --help
```

Downloading hourly counts for one segment
```bash
> telraam-data-manager download 9000002131 --start-date 2022-01-01 --end-date 2022-03-01 --output-path ./data/mydata.csv 
```

### API
Downloading hourly counts for one segment and plotting weekly average counts

```python
from telraam_data import download_one_segment
import datetime as dt
import matplotlib.pyplot as plt
data = download_one_segment(
    segment_id=90000002131,
    start_date=dt.date(2022, 1, 1),
    end_date=dt.date(2022, 3, 1),
    out_filepath="./data/mydata.csv"
)
data.resample('1D').sum().resample('7D').mean().plot(y='car')
plt.show()
```

## Installation

If you have a working version of Python on your system, you can install the package using:

```python
pip install telraam-data
```

Since Telraam-API v1, you need to supply an API access token in order to download data from the
Telraam database. You can create your personal token through your online
[Telraam dashboard](https://www.telraam.net/en/admin/mijn-eigen-telraam/tokens)
(even if you don't have a Telraam sensor yourself). More info at <https://telraam-api.net>.

When you have an API access token, set the corresponding environment variable using

```bash
export TELRAAM_API_TOKEN=<your access token>
```

Now you can start using this library!

## Notes
* This is a third-party package not officially affiliated with the Telraam project.
* The Telraam API is documented at https://telraam-api.net
* Telraam's data is made available under the CC BY 4.0 license. Thanks Telraam!
