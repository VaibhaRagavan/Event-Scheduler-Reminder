import json
import boto3
import os

cognito = boto3.client('cognito-idp')


cors_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS, GET, PUT, DELETE',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

USER_POOL_ID = os.environ.get('USER_POOL_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')

def lambda_handler(event, context):
    try:
        httpMethod = event['requestContext']['http']['method']

        # Handle CORS Preflight
        if httpMethod == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": "CORS preflight"
            }

        if httpMethod == "POST":
            body = json.loads(event['body'])
            email = body.get('email')
            code = body.get('code')

            if not email or not code:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'response': 'Email and confirmation code are required'})
                }

            # Confirm user with Cognito
            cognito.confirm_sign_up(
                ClientId=CLIENT_ID,
                Username=email,
                ConfirmationCode=code
            )

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'Account confirmed successfully'})
            }

        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'response': 'Method not allowed'})
        }

    except cognito.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': json.dumps({'response': 'User not found'})
        }
    except cognito.exceptions.CodeMismatchException:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'response': 'Invalid confirmation code'})
        }
    except cognito.exceptions.ExpiredCodeException:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'response': 'Confirmation code has expired'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'response': f'An error occurred: {str(e)}'})
        }
