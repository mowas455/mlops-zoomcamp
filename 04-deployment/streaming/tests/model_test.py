import model


def test_prepare_features():
    model_service = model.SteamingModelService(model_version=None, model=None)
    
    ride = {
        'PULocationID': 130,
        'DOLocationID': 205,
        'trip_distance': 3.66
    }

    actual_result = model_service.prepare_features(ride)
    expected_result = {
        'PU_DO': '130_205',
        'trip_distance': 3.66
    }

    assert actual_result == expected_result


class MockModel:

    def __init__(self, value):
        self.value = value

    def predict(self, features):
        n = len(features)
        return [self.value] * n


def test_predict():
    model_mock = MockModel(10.0)

    model_service = model.SteamingModelService(
        model_version='123',
        model=model_mock
    )

    features = {
        'PU_DO': '130_205',
        'trip_distance': 3.66
    }

    actual_result = model_service.predict(features)
    expected_result = 10.0

    assert actual_result == expected_result


def test_lambda_handler():
    test_data = "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ=="

    event = {
        "Records": [{
            "kinesis": {
                "data": test_data,
            }
        }]
    }

    model_mock = MockModel(10.0)

    model_service = model.SteamingModelService(
        model_version='123',
        model=model_mock
    )

    actual_result = model_service.lambda_handler(event)

    expected_result = {
        'predictions': [{
            'model': 'ride_duration_prediction_model',
            'version': '123',
            'prediction': {
                'ride_duration': 10.0,
                'ride_id': 256   
            }
        }]
    }

    assert actual_result == expected_result


def test_lambda_handler_callback():
    test_data = "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDI1NgogICAgfQ=="

    event = {
        "Records": [{
            "kinesis": {
                "data": test_data,
            }
        }]
    }

    model_mock = MockModel(10.0)

    results = []

    def test_callback(prediction_event):
        results.append(prediction_event)

    model_service = model.SteamingModelService(
        model_version='123',
        model=model_mock,
        callbacks=[test_callback]
    )

    model_service.lambda_handler(event)

    expected_prediction_event = {
        'model': 'ride_duration_prediction_model',
        'version': '123',
        'prediction': {
            'ride_duration': 10.0,
            'ride_id': 256   
        }
    }

    assert expected_prediction_event == results[0]
    assert len(results) == 1


