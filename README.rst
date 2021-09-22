telraam-data
=============

**A friendly Python package to download traffic count data from Telraam.net.**

The *telraam_data* package enables you to retrieve traffic count data from the
`Telraam Project <https://telraam.net>`_ API into ``pandas.DataFrame`` objects.


Examples
--------

Downloading hourly counts for one segment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  from telraam_data import download_segment
  import openpyxl
  data = download_segment(segment_id=9000000641)
  data.to_excel("counts.xlsx")


Downloading daily counts for multiple segments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  from telraam_data import download_segment
  data = download_segment(segment_id=[9000000641, 651160])
  data.to_csv("counts.csv")


Plotting weekly average counts for one segment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  from telraam_data import download_segment
  import matplotlib.pyplot as plt
  data = download_segment(9000000641,
                          time_start="2021-01-01 00:00:00Z",
                          time_end="2021-03-01 00:00:00Z")
  weekly_average = data.set_index('date').resample('1D').sum().resample('7D').mean() * 7
  weekly_average.plot(y=["car", "bike", "pedestrian"], marker='o')
  plt.plot()


Installation
------------

If you have a working version of Python on your system, you can install the package using:

.. code-block:: bash

  pip install telraam-data

Since Telraam-API v1, you need to supply an API access token in order to download data from the
Telraam database. You can create your personal token through your online Telraam dashboard
(even if you don't have a Telraam sensor yourself). More info at `<https://telraam-api.net>`_.

When you have an API access token, set the corresponsing environment variable using

.. code-block:: bash

  export TELRAAM_API_TOKEN=<your access token>

Now you can start using this library!

Notes
-----

* This is a third-party package not officially affiliated with the Telraam project.
* The Telraam API is documented at `<https://telraam-api.net>`_.
* Telraam's data is made available under the CC BY 4.0 license. Thanks Telraam!
