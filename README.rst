telraam-data
=============

**A friendly package to download traffic count data from the Telraam API.**

*telraam_query* is a Python package to retrieve traffic count data from the
`Telraam Project <https://telraam.net/>`_ as a Pandas DataFrame object.


Installation
------------

.. code-block:: bash

  pip install telraam_query


Examples
--------

Download hourly traffic counts for one segment:

.. code-block:: python

  from telraam_data import download_segment
  data = download_segment(segment_id=1003073114, fmt="per-hour")
  data.to_excel("hourly-counts.xls")


Download daily counts for all segments:

.. code-block:: python

  data = download_segment(segment_id="all", fmt="per-day")
  data.to_csv("daily-counts.csv")


Plot weekly average counts:

.. code-block:: python

  data = download_segment("all", time_start="2020-01-01 00:00:00Z",
                          time_end="2021-01-01 00:00:00Z", fmt="per-day")
  weekly_average = data.set_index('date').resample('7D').mean() * 7
  weekly_average.plot(y=["car", "bike", "pedestrian"], marker='o')


Notes
-----

This is a third-party package not officially affiliated with the Telraam project.
The Telraam API is documented at `https://telraam-api.net`_.
The data is made available under the CC BY 4.0 license.
