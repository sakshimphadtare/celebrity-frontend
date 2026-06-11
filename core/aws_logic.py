import boto3
import uuid
import base64
import json
from datetime import datetime

# AWS Clients
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
eventbridge = boto3.client('events')
s3 = boto3.client('s3')

# DynamoDB Table
table = dynamodb.Table('celebrity-data-123')

# SNS Topic ARN
TOPIC_ARN = 'arn:aws:sns:ap-south-1:231143200954:celebrity-alerts'

# Upload Bucket
UPLOAD_BUCKET = 'celebrity-upload-images-sakshi'


# =========================================================
# MAIN FUNCTION USED BY DJANGO
# =========================================================
def process_celebrity_image(image_base64, file_name):

    try:

        # -------------------------------
        # CLEAN BASE64 INPUT
        # -------------------------------
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        # Fix padding issue
        image_base64 += "=" * (-len(image_base64) % 4)

        # Decode image
        image_bytes = base64.b64decode(image_base64)

        print("IMAGE SIZE:", len(image_bytes))

        # -------------------------------
        # Upload to S3
        # -------------------------------
        s3.put_object(
            Bucket=UPLOAD_BUCKET,
            Key=file_name,
            Body=image_bytes
        )

        # -------------------------------
        # Rekognition (FIXED)
        # -------------------------------
        response = rekognition.recognize_celebrities(
            Image={
                'Bytes': bytes(image_bytes)
            }
        )

        celebrities = response.get("CelebrityFaces", [])

        if not celebrities:
            return {
                "status": "no_celebrity",
                "message": "No celebrity detected"
            }

        celeb = celebrities[0]
        celeb_name = celeb["Name"]
        confidence = celeb["MatchConfidence"]

        # -------------------------------
        # Save to DynamoDB
        # -------------------------------
        table.put_item(
            Item={
                "image_id": str(uuid.uuid4()),
                "image_name": file_name,
                "celebrity_name": celeb_name,
                "confidence": str(confidence),
                "timestamp": str(datetime.utcnow())
            }
        )

        # -------------------------------
        # EventBridge Trigger
        # -------------------------------
        eventbridge.put_events(
            Entries=[
                {
                    "Source": "celebrity.app",
                    "DetailType": "CelebrityDetected",
                    "Detail": json.dumps({
                        "celebrity_name": celeb_name
                    })
                }
            ]
        )

        return {
            "status": "success",
            "celebrity_name": celeb_name,
            "confidence": confidence
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# OPTIONAL: S3 TRIGGER FLOW (Lambda use)
# =========================================================
def process_s3_event(event):

    record = event['Records'][0]

    bucket = record['s3']['bucket']['name']
    image = record['s3']['object']['key']

    response = rekognition.recognize_celebrities(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': image
            }
        }
    )

    return {
        "status": "s3_trigger",
        "response": response
    }