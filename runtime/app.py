import uuid
import json
from random import randint
import os
import boto3
from boto3.session import Session
from boto3.dynamodb.types import TypeDeserializer
from chalice import Chalice, CORSConfig
from chalice.app import DynamoDBEvent, WebsocketEvent

app = Chalice(app_name="chaliceCdkTEST")
dynamodb = boto3.resource("dynamodb")
dynamodb_table = dynamodb.Table(os.environ.get("APP_TABLE_NAME", ""))
stream_arn = os.environ.get("DYNAMODB_STREAM_ARN", "")
deserializer = TypeDeserializer()

app.experimental_feature_flags.update(
    [
        "WEBSOCKETS",
    ]
)
app.websocket_api.session = Session()
client = boto3.client("events")
REACT_APP_WEBSOCKET_URL = "do931hqq8f.execute-api.eu-west-1.amazonaws.com"

cors_config = CORSConfig(
    allow_origin="http://localhost:3000",
)


@app.route("/virus", methods=["POST"], cors=cors_config)
def create_virus():
    virusId = str(uuid.uuid4())
    item = {
        "PK": "Virus",
        "SK": virusId,
    }
    dynamodb_table.put_item(Item=item)


@app.route("/virus", methods=["POST"], cors=cors_config)
def create_virus_http():
    create_virus()


@app.route("/virus", methods=["GET"], cors=cors_config)
def get_virus():
    items = dynamodb_table.query(
        KeyConditionExpression="PK = :PK", ExpressionAttributeValues={":PK": "Virus"}
    )["Items"]
    return json.dumps({"viruses": list(map(lambda item: {"id": item["SK"]}, items))})


@app.route("/virus/{id}", methods=["DELETE"], cors=cors_config)
def delete_virus(id):
    key = {
        "PK": "Virus",
        "SK": id,
    }
    dynamodb_table.delete_item(Key=key)


@app.on_ws_connect()
def connect(event: WebsocketEvent):
    item = {
        "PK": "Connection",
        "SK": event.connection_id,
    }
    dynamodb_table.put_item(Item=item)


@app.on_ws_disconnect()
def disconnect(event: WebsocketEvent):
    key = {
        "PK": "Connection",
        "SK": event.connection_id,
    }
    dynamodb_table.delete_item(Key=key)


def is_virus(item: "dict[str, str]"):
    return item["PK"] == "Virus"


def send_message_to_each_connection(virus_id: str):
    items = dynamodb_table.query(
        KeyConditionExpression="PK = :PK",
        ExpressionAttributeValues={":PK": "Connection"},
    )["Items"]
    for item in items:
        try:
            app.websocket_api.send(item["SK"], json.dumps({"virusId": virus_id}))
        except:
            key = {
                "PK": "Connection",
                "SK": item["SK"],
            }
            dynamodb_table.delete_item(Key=key)


@app.on_dynamodb_record(stream_arn=stream_arn)
def send_message(event: DynamoDBEvent):
    app.websocket_api.configure(REACT_APP_WEBSOCKET_URL, "api")
    for event_received in event:
        if event_received.event_name == "INSERT":
            print(event_received.new_image)
            new_item = {
                k: deserializer.deserialize(v)
                for k, v in event_received.new_image.items()
            }
            print(is_virus(new_item))
            if is_virus(new_item):
                return send_message_to_each_connection(new_item["SK"])


@app.lambda_function(name="ChooseWaitTime")
def choose_wait_time(event, context):
    return randint(0, 60)


@app.lambda_function(name="CreateVirus")
def create_virus_step_function(event, context):
    create_virus()


@app.schedule("rate(1 minute)")
def spread_virus(event):
    response = client.put_events(
        Entries=[
            {
                "EventBusName": "eventBus",
                "Source": "Time",
                "DetailType": "VIRUS_CREATION_REQUESTED",
                "Detail": json.dumps({}),
            }
        ]
    )
    print(response)
