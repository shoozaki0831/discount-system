import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('discount_history')

BUCKET_NAME = 'ozaki-discount-data'
FILE_NAME = 'discount_data.json'

def lambda_handler(event, context):
    # S3 の JSON を読み込む
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
    data = json.loads(obj['Body'].read().decode('utf-8'))

    today = datetime.now().date()

    for item in data:
        stay_date = datetime.strptime(item['date'], "%Y-%m-%d").date()
        diff = (stay_date - today).days

        original_price = item['price']

        # ★ 割引ロジック（2日以内なら 10% オフ）
        if diff <= 2:
            discounted_price = int(original_price * 0.9)
        else:
            discounted_price = original_price

        # DynamoDB に保存（履歴として残す）
        table.put_item(
            Item={
                'room': item['room'],
                'date': item['date'],
                'original_price': original_price,
                'discounted_price': discounted_price
            }
        )

    return {"status": "OK"}
