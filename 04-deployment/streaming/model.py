import json
import boto3
import base64

import mlflow


def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    ride_event = json.loads(decoded_data)
    return ride_event


class SteamingModelService:

    def __init__(self, model_version, model, callbacks=None):
        self.model_version = model_version
        self.model = model
        self.callbacks = callbacks or []

    def prepare_features(self, ride):
        features = {}
        features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
        features['trip_distance'] = ride['trip_distance']
        return features

    def predict(self, features):
        preds = self.model.predict(features)
        return float(preds[0])

    def lambda_handler(self, event):
        predictions_events = []
        
        for record in event['Records']:
            encoded_data = record['kinesis']['data']
            ride_event = base64_decode(encoded_data)

            ride = ride_event['ride']
            ride_id = ride_event['ride_id']

            features = self.prepare_features(ride)
            prediction = self.predict(features)
        
            prediction_event = {
                'model': 'ride_duration_prediction_model',
                'version': self.model_version,
                'prediction': {
                    'ride_duration': prediction,
                    'ride_id': ride_id   
                }
            }

            for callback in self.callbacks:
                callback(prediction_event)

            predictions_events.append(prediction_event)

        return {
            'predictions': predictions_events
        }


class KinesisStream:
    def __init__(self, kinesis_client, kinesis_stream):
        self.kinesis_client = kinesis_client
        self.kinesis_stream = kinesis_stream

    def put_record(self, prediction_event):
        ride_id = prediction_event['prediction']['ride_id']
        self.kinesis_client.put_record(
            StreamName=self.kinesis_stream,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id)
        )


def load_model(run_id):
    logged_model = f's3://mlflow-models-alexey/1/{run_id}/artifacts/model'
    model = mlflow.pyfunc.load_model(logged_model)
    return model


def init(
        prediction_stream_name: str,
        run_id: str,
        test_run: str
    ):

    kinesis_client = boto3.client('kinesis')
    mlflow_model = load_model(run_id)

    kinesis_callback = KinesisStream(
        kinesis_client=kinesis_client,
        kinesis_stream=prediction_stream_name
    )

    model_service = SteamingModelService(
        model_version=run_id,
        model=mlflow_model,
        callbacks=[kinesis_callback.put_record]
    )

    return model_service