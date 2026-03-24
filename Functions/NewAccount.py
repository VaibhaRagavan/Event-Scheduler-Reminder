import json
import boto3
import os
import uuid
from boto3.dynamodb.conditions import Key


# Initialize Cognito and DynamoDB clients
cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

# Get environment variables for the User Pool ID and App Client ID
USER_POOL_ID = os.environ.get('USER_POOL_ID') 
CLIENT_ID = os.environ.get('CLIENT_ID')  

# DynamoDB table reference
table = dynamodb.Table('User_details')
GSI_NAME = 'phone-index'

cors_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

def lambda_handler(event, context):
    # Check if environment variables are set
    if not USER_POOL_ID or not CLIENT_ID:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Missing environment variables for USER_POOL_ID or CLIENT_ID'})
        }
    
    try:
        # Safely extract HTTP method
        print(event)
        httpMethod = event['requestContext']['http']['method']
        print(httpMethod)
        
        # Handle CORS Preflight
        if httpMethod == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": "CORS preflight"
            }

        # Handle POST (register new user)
        if httpMethod == "POST":
            body = json.loads(event['body'])
            username = body.get('name')
            email = body.get('email')
            password = body.get('password')
            dob = body.get('dob')
            phone=body.get('phonenumber')

            if not username or not email or not password or not dob or not phone:
             return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'response': 'All fields are required'})
                }
            
            # Register the user with Cognito
            try:
                signup_response = cognito.sign_up(
                    ClientId=CLIENT_ID,
                    Username=email,
                    Password=password,
                    UserAttributes=[
                        {'Name': 'email', 'Value': email},
                        {'Name': 'given_name', 'Value': username},
                        {'Name': 'birthdate', 'Value': dob},
                         {'Name': 'phone_number', 'Value': phone}
                    ]
                )

                # Generate a unique user ID for DynamoDB
                user_id = str(uuid.uuid4())
                # Check if user details already exist in DynamoDB
                dynamodb_response=table.query(
                    IndexName=GSI_NAME,
                    KeyConditionExpression=Key('phone').eq(phone)
                )
                if 'Items' in dynamodb_response and dynamodb_response['Items']:
                    # Update existing user details
                    new_email = email
                    old_item = dynamodb_response['Items'][0]
                    old_email = old_item['email']
                    new_username= username
                    new_dob=dob
                    new_item = {
                        'email': new_email,  
                        'phone': old_item['phone'],
                        'userid': old_item.get('userid', str(uuid.uuid4())),
                        'username': new_username,
                        'dob':new_dob}
                    table.put_item(Item=new_item)
                    table.delete_item(Key={'email': old_email})
  
                    return {
                        'statusCode': 200,
                        'headers': cors_headers,
                        'body': json.dumps({'message':'User details updated '})
                    }
                else:
                    # Store additional user data in DynamoDB
                    table.put_item(
                    Item={
                        'phone':phone,
                        'email': email,
                        'userid': user_id,
                        'username': username,
                        'dob': dob,
                        
                        
                    }
                )

                # Logging DynamoDB Response
                print("=== DynamoDB Response ===")
                print(json.dumps(dynamodb_response))

                return {
                    'statusCode': 200,
                    'headers': cors_headers,
                    'body': json.dumps({'message': 'User created successfully'})
                }

            except cognito.exceptions.UsernameExistsException:
                return {
                    'statusCode': 409,
                    'headers': cors_headers,
                    'body': json.dumps({'response': 'Email already exists'})
                }
            except cognito.exceptions.InvalidPasswordException:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'response': 'Password does not meet policy requirements'})
                }
            except Exception as e:
                # Handle general exception and log error
                print("=== ERROR ===")
                print(str(e))
                return {
                    'statusCode': 500,
                    'headers': cors_headers,
                    'body': json.dumps({'response': f'Error during user registration: {str(e)}'})
                }

        # Method not allowed
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'response': 'Method not allowed'})
        }

    except Exception as e:
        # Log any top-level exceptions
        print("=== ERROR ===")
        print(str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }
