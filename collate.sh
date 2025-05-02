#!/bin/bash

STUDENT_ID="017721457"
REGION="us-west-2"
POPULATOR_LAMBDA="queue-populator-${STUDENT_ID}"
OUTPUT_BUCKET="cs218-final-code-bucket-${STUDENT_ID}"
CSV_PREFIX="csv_files/"
TMP_DIR="./tmp_csvs"
FINAL_OUTPUT="collated_output.csv"

#Call Lambda function
echo "Invoking queue-populator Lambda..."
QUEUE_URL=$(aws sqs get-queue-url \
  --queue-name cs218-final-queue-${STUDENT_ID} \
  --region $REGION \
  --output text)

aws lambda invoke \
  --function-name "$POPULATOR_LAMBDA" \
  --region "$REGION" \
  --cli-binary-format raw-in-base64-out \
  --payload "{\"input_bucket\":\"cs218-final-input-bucket-${STUDENT_ID}\",\"output_bucket\":\"${OUTPUT_BUCKET}\",\"queue_url\":\"${QUEUE_URL}\"}" \
  response.json


echo "Waiting 60 seconds for processing..."
sleep 60

#Download all CSV files from S3 to /tmp_csvs in local
echo "Downloading CSV files..."
mkdir -p $TMP_DIR
aws s3 cp s3://$OUTPUT_BUCKET/$CSV_PREFIX $TMP_DIR --recursive --exclude "*" --include "*.csv"

#Merging all CSVs into one
echo "Collating CSVs..."
header_written=false
> $FINAL_OUTPUT

find $TMP_DIR -type f -name "*.csv" | while read csv_file; do
  if [ "$header_written" = false ]; then
    cat "$csv_file" >> $FINAL_OUTPUT
    header_written=true
  else
    tail -n +2 "$csv_file" >> $FINAL_OUTPUT
  fi
done

echo "Collation complete: $FINAL_OUTPUT"
