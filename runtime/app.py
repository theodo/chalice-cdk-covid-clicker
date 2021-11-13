import os
import uuid
import boto3
import json
from boto3.session import Session
from boto3.dynamodb.types import TypeDeserializer
from chalice import Chalice,CORSConfig
from chalice.app import DynamoDBEvent, WebsocketEvent, CloudWatchEvent

app = Chalice(app_name='chaliceCdkTEST')
dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(os.environ.get('APP_TABLE_NAME', ''))
stream_arn = os.environ.get('DYNAMODB_STREAM_ARN', '')
deserializer = TypeDeserializer()

app.experimental_feature_flags.update([
    'WEBSOCKETS',
])
app.websocket_api.session = Session()

# EXAMPLES
# @app.route('/users', methods=['POST'])
# def create_user():
#     request = app.current_request.json_body
#     item = {
#         'PK': 'User#%s' % request['username'],
#         'SK': 'Profile#%s' % request['username'],
#     }
#     item.update(request)
#     dynamodb_table.put_item(Item=item)
#     return {}


# @app.route('/users/{username}', methods=['GET'])
# def get_user(username):
#     key = {
#         'PK': 'User#%s' % username,
#         'SK': 'Profile#%s' % username,
#     }
#     item = dynamodb_table.get_item(Key=key)['Item']
#     del item['PK']
#     del item['SK']
#     return item

cors_config = CORSConfig(
    allow_origin='http://localhost:3000',
)

@app.route('/virus', methods=['POST'],cors=cors_config)
def create_virus():
    virusId = str(uuid.uuid4());
    item = {
        'PK': 'Virus',
        'SK': virusId,
    }
    dynamodb_table.put_item(Item=item)
    return {}

@app.route('/virus', methods=['GET'],cors=cors_config)
def get_virus():
    items = dynamodb_table.query(
        KeyConditionExpression='PK = :PK',
        ExpressionAttributeValues={':PK': 'Virus'}
        )['Items']
    return json.dumps({'viruses':list(map(lambda item: {'id':item['SK']},items))})

@app.route('/virus/{id}', methods=['DELETE'],cors=cors_config)
def delete_virus(id):
    key = {
        'PK': 'Virus',
        'SK': id,
    }
    dynamodb_table.delete_item(Key=key)
    return {}

@app.on_ws_connect()
def connect(event:WebsocketEvent):
    item = {
        'PK': 'Connection',
        'SK': event.connection_id,
    }
    dynamodb_table.put_item(Item=item)
    return {}

@app.on_ws_disconnect()
def disconnect(event:WebsocketEvent):
    key = {
        'PK': 'Connection',
        'SK': event.connection_id,
    }
    dynamodb_table.delete_item(Key=key)
    return {}

def is_virus(item: 'dict[str, str]'):
    if item['PK']=='Virus':
        return True
    else:
        return False

def send_message_to_each_connection(virus_id:str):
    items = dynamodb_table.query(
        KeyConditionExpression='PK = :PK',
        ExpressionAttributeValues={':PK': 'Connection'}
        )['Items']
    for item in items:
        print(item)
        try:
            app.websocket_api.send(item['SK'],json.dumps({'virusId':virus_id}))
        except:
            key = {
                'PK': 'Connection',
                'SK': item['SK'],
            }
            dynamodb_table.delete_item(Key=key)

    
@app.on_dynamodb_record(stream_arn=stream_arn)
def send_message(event:DynamoDBEvent):
    app.websocket_api.configure("do931hqq8f.execute-api.eu-west-1.amazonaws.com","api")
    for eventReceived in event:
        if eventReceived.event_name=='INSERT':
            print(eventReceived.new_image)
            new_item = {k: deserializer.deserialize(v) for k, v in eventReceived.new_image.items()}
            print(is_virus(new_item))
            if is_virus(new_item):
                return send_message_to_each_connection(new_item['SK'])


# cw_event = cloudwatch event = event bridge
# The rule will be created in the default event bus
# It's currently not possible to use an other bus
# https://github.com/aws/chalice/issues/1755
@app.on_cw_event(event_pattern={"detail-type": ["test-event-bridge"]})
def print_event(event: CloudWatchEvent):
    print(event.to_dict())
