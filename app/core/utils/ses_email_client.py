# pip install boto3

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask import current_app


def get_ses_client():
    return boto3.client(
        'ses',
        region_name= current_app.config['AWS_SES_REGION'],
        aws_access_key_id=current_app.config['AWS_SES_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SES_SECRET_KEY']
    )


def send_email(subject, body, to_addresses, from_address):
    ses_client = get_ses_client()
    try:
        response = ses_client.send_email(
            Source=from_address,
            Destination={
                'ToAddresses': to_addresses
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body
                    }
                }
            }
        )
        return response
    except (NoCredentialsError, ClientError) as e:
        print(e)
        return None
