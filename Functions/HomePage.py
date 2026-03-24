import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('User_details')

cros_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

def lambda_handler(event, context):
    print(event)
    http_method = event['requestContext']['http']['method']

    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cros_headers,
            'body': json.dumps("CORS preflight")
        }

    if http_method == 'POST':
        body = json.loads(event['body'])
        email = body.get('email')
        print(f"Received email: {email}")

        try:
            response = table.get_item(Key={'email': email})
            print(f"DynamoDB response: {response}")
            name = response['Item']['username']
            print(f"Retrieved name: {name}")
            
            # You can customize this based on what you actually want to return
            return {
                'statusCode': 200,
                'headers': cros_headers,
                'body': json.dumps({'response': name})
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'statusCode': 500,
                'headers': cros_headers,
                'body': json.dumps({'error': str(e)})
            }

    return {
        'statusCode': 405,
        'headers': cros_headers,
        'body': json.dumps({'error': 'Method Not Allowed'})
    }
