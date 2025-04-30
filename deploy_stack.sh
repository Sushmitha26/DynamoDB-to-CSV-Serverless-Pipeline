#!/bin/bash

STUDENT_ID="017721457"
S3_CODE_BUCKET="cs218-final-code-bucket-${STUDENT_ID}"

aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket ${S3_CODE_BUCKET} \
    --output-template-file packaged-template.yaml

aws cloudformation deploy \
  --template-file packaged-template.yaml \
  --stack-name cs218-final-resources \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-west-2
