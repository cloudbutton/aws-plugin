# Cloud Button AWS Lambda Plugin
Cloudbutton toolkit plugin for Amazon Lambda and Amazon S3

- CloudButton Project: [http://cloudbutton.eu/](http://cloudbutton.eu/)
- CloudButton Toolkit Github: [https://github.com/cloudbutton/cloudbutton](https://github.com/cloudbutton/cloudbutton)

### AWS Account Setup

 1. [Login](https://console.aws.amazon.com/?nc2=h_m_mc) to Amazon Web Services Console (or signup if you don't have an account)
 2. Navigate to *IAM > Roles*. Click on *Create Role*.
 3. Select *Lambda* and then click *Next: Permissions*.
 4. Type `s3` at the search bar and select *AmazonS3FullAccess*. Type `lambda` at the search bar and select *AWSLambdaFullAccess*. Click on *Next: Tags* and then *Next: Review*.
 5. Type a role name, for example `cloudbutton-execution-role`. Click on *Create Role*.
 6. Navigate to *S3*. Click *Create Bucket*. Type a name (e.g. `cloudbutton-data`). Select a *Region*. The Lambda functions will be invoked at the same region. Fianlly click *Create*.

**Note:**  If you don't have permission to create new roles, ask your account admin to do it for you.

### Local Configuration

Copy the following lines and paste them to the local configuration file located in your home directory called `.cloudbutton_config`

```yaml
aws:
    access_key_id : <ACCESS_KEY_ID>
    secret_access_key : <SECRET_ACCESS_KEY>

aws_lambda:
    execution_role : <EXECUTION_ROLE_ARN>
    region_name : <REGION_NAME>

aws_s3:
    endpoint : <S3_ENDPOINT_URI>
```

 - `access_key_id` and `secret_access_key`: Keys to access to all AWS services from your account. To find them, navigate to *My Security Credentials* and click *Create Access Key* if you don't already have one.
 - `region_name`: Region where the S3 bucket is located and where Lambda functions will be invoked (e.g. `us-east-1`).
 - `execution_role`: ARN of the execution role created at step 2. You can find it in the Role page at the *Roles* list in the *IAM* section (e.g. `arn:aws:iam::1234567890:role/cloudbutton-role`).
- `endpoint`: Endpoint URL of the bucket created at step 6 (e.g. `https://s3.us-east-1.amazonaws.com`)

### Usage

To use AWS Lambda, change the following lines of your local configuration file:
```yaml
    compute_backend : 'aws_lambda'
    storage_backend: 'aws_s3'
```
