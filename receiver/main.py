import json
from datetime import datetime

import boto3
import botocore

from ical import Calendar, Event


class Storage:
    def __init__(self, bucket_name: str):
        self.bucket = bucket_name
        self.client = boto3.session.Session().client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
        )

        try:
            self.client.create_bucket(Bucket=self.bucket)
        except botocore.exceptions.ClientError:
            pass

    def get(self, key: str) -> str:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=key)
        except botocore.exceptions.ClientError:
            return ''

        return obj['Body'].read().decode('utf-8')

    def put(self, key: str, content: str):
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)


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

    storage = Storage(f'functions-{context.function_name}')

    calendar = Calendar.from_ical(storage.get('calendar.ics'))

    for session in body['sleep_sessions']:
        event = Event(session['id'], 'Sleep', parse_date(session['start_date']), parse_date(session['end_date']))
        calendar.add_event(event)

    storage.put('calendar.ics', calendar.generate_ical())
    
    return {
        'statusCode': 200,
        'body': 'Done',
    }


def parse_date(date: datetime):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
