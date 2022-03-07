import telraam_data.query as query
import datetime
import random


def test_query_active_segments():
    response = query.query_active_segments()
    assert response["status_code"] == 200
    assert response["message"] == "ok"
    assert response["type"] == "FeatureCollection"
    num_segments = len(response["features"])
    assert num_segments > 0
    idx = random.randrange(1, num_segments) - 1
    assert response["features"][idx]["type"] == "Feature"
    assert response["features"][idx]["geometry"]["type"] == "MultiLineString"
    assert "properties" in response["features"][idx].keys()


def test_query_active_segments_in_radius():
    # Choose a random segment from the database and use its coordinates
    response = query.query_active_segments()
    all_segments = response["features"]
    segment_idx = random.randrange(1, len(all_segments)) - 1
    segment_coordinates = all_segments[segment_idx]["geometry"]["coordinates"]
    lon, lat = segment_coordinates[0][0]

    # From that coordinate, search in a 1 km radius. There must be at least one device.
    response = query.query_active_segments_in_radius(lon, lat, 1)
    assert response["status_code"] == 200
    assert response["message"] == "ok"
    assert response["type"] == "FeatureCollection"
    assert len(response["features"]) > 0


def test_query_one_segment():
    # Choose a random segment from the database
    all_segments = query.query_active_segments()
    segment_idx = random.randrange(1, len(all_segments)) - 1
    segment = all_segments["features"][segment_idx]
    segment_id = segment["properties"]["segment_id"]
    segment_last_time = segment["properties"]["last_data_package"]

    # Query that segment for the last live day
    time2 = datetime.datetime.strptime(segment_last_time, "%Y-%m-%d %H:%M:%S.%f%z")
    time1 = time2 - datetime.timedelta(days=1)
    response = query.query_one_segment(segment_id, str(time1), str(time2))

    assert response["status_code"] == 200
    assert response["message"] == "ok"
    num_reports = len(response["report"])
    assert num_reports > 0

    # All listed keys must exist in the queried report
    report_idx = random.randrange(1, num_reports) - 1
    report = response["report"][report_idx]
    required_keys = [
        'instance_id', 'segment_id', 'date', 'interval', 'uptime', 'heavy', 'car', 'bike', 'pedestrian', 'heavy_lft',
        'heavy_rgt', 'car_lft', 'car_rgt', 'bike_lft', 'bike_rgt', 'pedestrian_lft', 'pedestrian_rgt', 'direction',
        'car_speed_hist_0to70plus', 'car_speed_hist_0to120plus', 'timezone', 'v85'
    ]
    assert set(required_keys) == set(required_keys).intersection(report.keys())

