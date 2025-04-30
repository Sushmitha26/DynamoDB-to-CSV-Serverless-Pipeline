import boto3, json, csv, gzip, os
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from datetime import datetime

def download_and_decompress_file(bucket_name, key, download_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, key, download_path)
    records = []
    with gzip.open(download_path, 'rt') as f_in:
        for line in f_in:
            if line.strip():  # Ensure it's not an empty line
                records.append(json.loads(line))
    return records

def from_dynamodb_to_json(item):
    d = TypeDeserializer()
    return {k: d.deserialize(value=v) for k, v in item.items()}

def convert_ddb_json_to_csv(all_records, schema, bucket_name, output_key):
    print(f"Converting ddb json to csv with columns: {schema}")

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    key = output_key

    os.makedirs('/tmp/ddb_to_csv_temp/', mode=0o774, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = f'/tmp/ddb_to_csv_temp/{key.split("/")[-1].split(".csv")[0]}_{timestamp}.csv'
    with open(temp_file, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=schema)
        writer.writeheader()
        for record in all_records:
            cleaned_record = from_dynamodb_to_json(record['Item'])
            writer.writerow(cleaned_record)

    bucket.upload_file(temp_file, key)

    if os.path.isfile(temp_file):
        os.remove(temp_file)

    return True

def handler(event, context):
    for message in event['Records']:
        message_body = json.loads(message['body'])
        json_gz_file = message_body['json_path']
        input_bucket = message_body['input_bucket']
        output_bucket = message_body['output_bucket']
        output_key = message_body['output_key']

        download_dir = '/tmp'

        print("Processing ddb json file: " + json_gz_file)
        print("Input bucket: " + input_bucket)
        print("Output bucket: " + output_bucket)
        print("Output key: " + output_key)

        download_path = os.path.join(download_dir, os.path.basename(json_gz_file))
        records = download_and_decompress_file(input_bucket, json_gz_file, download_path)

        print(f'Got {len(records)} records')

        schema = ['ID', 'Name', 'Value']

        success = convert_ddb_json_to_csv(records, schema, output_bucket, output_key)

        return {'success': success}

