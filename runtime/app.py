import os
import uuid
import boto3
from chalice import Chalice,CORSConfig

app = Chalice(app_name='chaliceCdkTEST')
dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(os.environ.get('APP_TABLE_NAME', ''))

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
    return items

@app.route('/virus/{id}', methods=['DELETE'],cors=cors_config)
def delete_virus(id):
    key = {
        'PK': 'Virus',
        'SK': id,
    }
    dynamodb_table.delete_item(Key=key)
    return {}

