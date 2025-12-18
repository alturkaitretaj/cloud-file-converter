import requests
import os

def lambda_handler(event, context):

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    filename = key.split(".")[0]

    print("File received:", bucket, key)

    flask_url = os.environ["FLASK_URL"].rstrip("/")
    url = f"{flask_url}/{filename}"

    response = requests.post(url)

    print("EC2 response:", response.status_code)
    print(response.text)

    return {
        "statusCode": response.status_code,
        "body": response.text
    }
