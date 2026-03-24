import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table('User_details')
event_table = dynamodb.Table('Event_details')

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
            response = user_table.get_item(Key={'email': email})
            
            userid = response['Item']['userid']
            print(f"Retrieved id: {userid}")
            response = event_table.query(
                 KeyConditionExpression=boto3.dynamodb.conditions.Key('userid').eq(userid)
            )
           
            items=response['Items']
            print(f"Retrieved items: {items}")
            events=[]
            for item in items:
                
                eventid = item['event_id']
                event_name=item['event_type']
                event_date=item['event_date']
                events_details={'eventid':eventid, 'event_type':event_name, 'eventdate':event_date}
                events.append(events_details)
            
            
            
            
            
            # You can customize this based on what you actually want to return
            return {
                'statusCode': 200,
                'headers': cros_headers,
                'body': json.dumps({'events': events })
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

    