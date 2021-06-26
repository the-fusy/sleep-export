import json
import boto3
from datetime import datetime

from ical import Calendar, Event


def publish_calendar(calendar: Calendar):
    s3 = boto3.session.Session().client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
    )
    s3.put_object(Bucket='...', Key='cal.ics', Body=calendar.generate_ical())


def handler(event, context):
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
        }

    body = json.loads(event['body'])

    error = body['error']
    if error is not None:
        return {
            'statusCode': 500,
            'body': error,
        }
    
    sleep_sessions = body['sleep_sessions']

    calendar = Calendar()
    for session in sleep_sessions:
        event = Event(
            session['id'],
            'Sleep',
            datetime.strptime(session['start_date'], '%Y-%m-%dT%H:%M:%SZ'),
            datetime.strptime(session['end_date'], '%Y-%m-%dT%H:%M:%SZ'),
        )
        calendar.add_event(event)
    publish_calendar(calendar)
    
    return {
        'statusCode': 200,
        'body': 'Done',
    }
