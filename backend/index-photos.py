import json
import boto3
import urllib3
from datetime import datetime

OS_DOMAIN = 'os domain examople 
OS_INDEX = 'photos'
OS_AUTH = ('example', 'exampe!') # Using the Master User we created in Milestone 1

# --- CLIENTS ---
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
http = urllib3.PoolManager()

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    
    # Loop through every file uploaded
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # 1. Detect Labels via Rekognition
        try:
            print(f"Analyzing {key} in {bucket}")
            response = rekognition.detect_labels(
                Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                MaxLabels=10,
                MinConfidence=75
            )
            labels = [label['Name'] for label in response['Labels']]
            print(f"Detected labels: {labels}")
        except Exception as e:
            print(f"Error detecting labels: {e}")
            continue

        # 2. Get S3 Metadata (Custom Labels)
        try:
            head_response = s3.head_object(Bucket=bucket, Key=key)
            # S3 metadata keys are always lowercased
            custom_labels = head_response.get('Metadata', {}).get('customlabels', '')
            
            if custom_labels:
                custom_list = [l.strip() for l in custom_labels.split(',')]
                labels.extend(custom_list)
                print(f"Added custom labels: {custom_list}")
        except Exception as e:
            print(f"Error getting metadata: {e}")

        # 3. Prepare JSON for OpenSearch
        document = {
            "objectKey": key,
            "bucket": bucket,
            "createdTimestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "labels": labels
        }
        
        # 4. Post to OpenSearch
        url = f'https://{OS_DOMAIN}/{OS_INDEX}/_doc/'
        headers = urllib3.make_headers(basic_auth=f"{OS_AUTH[0]}:{OS_AUTH[1]}")
        headers['Content-Type'] = 'application/json'
        
        encoded_data = json.dumps(document).encode('utf-8')
        
        try:
            response = http.request('POST', url, body=encoded_data, headers=headers)
            print(f"OpenSearch Status: {response.status}")
            print(f"OpenSearch Response: {response.data.decode('utf-8')}")
        except Exception as e:
            print(f"Error posting to OpenSearch: {e}")
            raise e

    return {'statusCode': 200, 'body': json.dumps('Indexing Complete')}