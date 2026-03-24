import boto3
import os
import json

cognito = boto3.client('cognito-idp')
CLIENT_ID = os.environ['CLIENT_ID']
cors_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

def lambda_handler(event, context):
    print(event)
    http_method = event['requestContext']['http']['method']
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps('Hello from Lambda!')
        }
    if http_method == 'POST':
        
        body = json.loads(event['body'])
        action = body.get('action') 
        email = body.get('email')

    try:
        if action == 'start':
            cognito.forgot_password(
                ClientId=CLIENT_ID,
                Username=email     
            )
            return {
                'statusCode': 200,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Verification code sent to email'})
            }

        elif action == 'confirm':
            code=body.get('code')
            new_password = body.get('new_password')

            cognito.confirm_forgot_password(
                ClientId=CLIENT_ID,
                Username=email,
                ConfirmationCode=code,
                Password=new_password
            )
            return {
                'statusCode': 200,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Password changed successfully'})
            }

        else:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Invalid action'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': str(e)})
        }
