import json
import boto3
import os

# Initialize Cognito client and DynamoDB resource
cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

# Get environment variables for the User Pool ID and App Client ID
USER_POOL_ID = os.environ.get('USER_POOL_ID')  
CLIENT_ID = os.environ.get('CLIENT_ID') 

# DynamoDB table reference
table = dynamodb.Table('User_details')

cors_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

def lambda_handler(event, context):

    print(json.dumps(event)) 
    try:
        # Safely extract HTTP method
        httpMethod = event['requestContext']['http']['method']
        
        # Handle CORS Preflight
        if httpMethod == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": "CORS preflight"
            }

        # Handle POST (login)
        if httpMethod == "POST":
            body = json.loads(event['body'])
            email = body.get('email')
            password = body.get('password')

            if not email or not password:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'response': 'Email and password required'})
                }

            # Authenticate user with Cognito
            try:
                auth_response = cognito.initiate_auth(
                    ClientId=CLIENT_ID,
                    AuthFlow='USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': email,
                        'PASSWORD': password
                    }
                )

                return {
                    'statusCode': 200,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'response': 'Login successful',
                        'token': auth_response['AuthenticationResult']['IdToken'],
                       
                    })
                }

            except cognito.exceptions.NotAuthorizedException:
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'response': 'Incorrect password'})
                }

            except cognito.exceptions.UserNotFoundException:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'response': 'User not found'})
                }

        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'response': 'Method not allowed'})
        }

    except Exception as e:
        print("=== ERROR ===")
        print(str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }
