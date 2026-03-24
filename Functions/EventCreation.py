import json
import boto3
import logging
import os
import uuid
from boto3.dynamodb.conditions import Key, Attr

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB resources
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Event_details')
table2 = dynamodb.Table('User_details')

# CORS headers
cors_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

def lambda_handler(event, context):
    try:
        httpMethod = event['requestContext']['http']['method']

        # CORS Preflight
        if httpMethod == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": "CORS preflight"
            }

        # Handle POST (create event)
        if httpMethod == "POST":
            body = json.loads(event['body'])
            
            logger.info(f"Received body: {body}")

            user_email = body['email']
            event_id = str(uuid.uuid4())
            event_type = body['event_type']
            event_date = body['event_date']
            reminde_me = body['remindme']
            post_public = body['post']
            recipient = body['persons']
            other_event_name=body['other_event_type']

            # Get user from User_details
            response = table2.get_item(Key={'email': user_email})
            if 'Item' not in response:
                return {
                    "statusCode": 404,
                    "headers": cors_headers,
                    "body": json.dumps({"error": "User not found"})
                }

            user_item = response['Item']
            user_id = user_item['userid']
            print(user_id)
            if event_type=='other':
                event_type=other_event_name
            item = {
                'userid': user_id,
                'event_id': event_id,
                'event_type': event_type,
                'event_date': event_date,
                'reminde_me': reminde_me,
                'post_public': post_public,
                'recipient': recipient,
                
            }

            # If reminder is requested, add extra info
            if str(reminde_me).strip()=='True':
                username = user_item.get('username', '')
                user_phone = user_item.get('phone', '')
                reminder_note = f"Hey {username}, you have a reminder for your {event_type} event on {event_date} From Wishpal."
                item['reminde_me_recipient']=[username, user_phone,reminder_note]
                logger.info(f"Reminder list added successfully for event: {event_id}")
            table.put_item(Item=item)
          
          

            #Create a entry in usertable 
            for people in recipient:
                if event_type=='anniversary':
                    name1=people['name1']
                    name2=people['name2']
                    phone1=people['phone1']
                    phone2=people['phone2']
                    email1 = f"{ name1 .lower().replace(' ', '')}@wishpal.in"  # Dummy email
                    email2 = f"{ name2 .lower().replace(' ', '')}@wishpal.in"  # Dummy email
                    existing_phone1 = table2.query(
                        IndexName='phone-index',  # Use your actual GSI name here
                        KeyConditionExpression=Key('phone').eq(people['phone1'])
                        )
                        # logger.info(f"Existing phone: {existing_phone1}")
                    existing_phone2 = table2.query(
                        IndexName='phone-index',  # Use your actual GSI name here
                        KeyConditionExpression=Key('phone').eq(people['phone2'])
                        )
                        # logger.info(f"Existing phone: {existing_phone2}")
                    if  existing_phone1.get("Items"):
                        logger.info(existing_phone1.get('Items'))
                        logger.info(f"User already exists")
                        continue
                        
                    else:
                        table2.put_item(Item={
                            'phone':phone1,
                            'email': email1,
                            'userid': str(uuid.uuid4()),
                            'username': name1,
                            'dob': event_date,
                        })
                        logger.info(f"User created successfully: {email1}")

                    if  existing_phone2.get("Items"):
                        logger.info(f"User already exists")
                        continue
                       
                    else:
                        table2.put_item(Item={
                            'phone':phone2,
                            'email': email2,
                            'userid': str(uuid.uuid4()),
                            'username': name2,
                            'dob': event_date,
                        })
                        logger.info(f"User created successfully: {email2}")

                else:
                    name = people['name'] 
                    phone = people['phone']
                    email = f"{ name .lower().replace(' ', '')}@wishpal.in"  # Dummy email
                    existing_phone = table2.query(
                    IndexName='phone-index',  # Use your actual GSI name here
                    KeyConditionExpression=Key('phone').eq(phone)
                    )
                    logger.info(f"Existing phone: {existing_phone}")
                
                    if  existing_phone.get("Items"):
                        logger.info(existing_phone.get('Items'))
                        logger.info(f"User already exists")
                        continue
                        
                    else:
                        item2={
                            'phone':phone,
                            'email': email,
                            'userid': str(uuid.uuid4()),
                            'username': name,
                            'dob': event_date,}
                        table2.put_item(Item=item2)
                        logger.info(f"User created successfully: {email}")
            
            
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({"message": "Event created successfully", "event_id": event_id})
            }
            

        # Method not allowed
        return {
            "statusCode": 405,
            "headers": cors_headers,
            "body": json.dumps({"error": "Method not allowed"})
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }
