from .. import list_segments, list_segments_by_coordinates


def test_list_segments():
    # As of April 2020 there were more than 900 active segments.
    segments = list_segments()
    assert len(segments) > 900


def test_list_segments_by_coordinates():
    # As of April 2020 there are more than 30 active segments in Schaarbeek
    segments = list_segments_by_coordinates(lat=50.867, lon=4.373, radius=2)
    assert len(segments) > 30
    # 1003073114 should be one of them
    assert 1003073114 in segments
    # 1003063473 should not be one of them
    assert 1003063473 not in segments
