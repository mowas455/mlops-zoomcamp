import model


def test_base64_decode():
    data = "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ=="
    actual_result = model.base64_decode(data)

    expected_result = {
        'ride': {
            'PULocationID': 130,
            'DOLocationID': 205,
            'trip_distance': 3.66
        },
        'ride_id': 256
    }

    assert actual_result == expected_result
