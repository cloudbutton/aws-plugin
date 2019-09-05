
# cloud-button-aws-plugin
Cloudbutton toolkit plugin for Amazon Lambda and Amazon S3

- CloudButton Project: [http://cloudbutton.eu/](http://cloudbutton.eu/)
- CloudButton Toolkit: [https://github.com/pywren/pywren-ibm-cloud](https://github.com/pywren/pywren-ibm-cloud)

### AWS Account Setup

 1. [Login](https://console.aws.amazon.com/?nc2=h_m_mc) to Amazon Web Services Console (or signup if you don't have an account)
 2. Click on you user name on the top right corner. Then click on *My security credentials* at the drop down menu.
 3. Click on *Roles* at the left menu. Then click on *Create Role*.
 4. Click on *Lambda*, then click *Next: Permissions*.
 5. Type `s3` at the search bar and select *AmazonS3FullAccess*.
 6. Type `lambda` at the search bar and select *AWSLambdaFullAccess*.
 7. Click on *Next: Tags* and then *Next: Review*.
 8. Type a role name, for example `cloudbutton-execution-role`.
 9. Click on *Create Role*.
 10. Click on *Services* at top left menu. Click on *S3* at the drop down menu.
 11. Click *Create Bucket*. Type a name (e.g. `cloudbutton-data`) and then click *Create*.
**Note:**  If you don't have access to create new roles, ask your account admin to do it for you.

### Local Configuration

Copy the following lines and paste them to the local configuration file located in your home directory called `.pywren_config`

```yaml
aws:
    access_key_id : <ACCESS_KEY_ID>
    secret_access_key : <SECRET_ACCESS_KEY>

aws_lambda:
    region_name : <REGION_NAME>
    execution_role : <EXECUTION_ROLE_ARN>

aws_s3:
    endpoint : <S3_ENDPOINT_URI>
```

 - `access_key_id` and `secret_access_key`: Keys to access to all AWS services from your account. To find them, navigate to *My Security Credentials* and click *Create Access Key* if you don't already have one.

 - `region_name`: Region where the S3 bucket is located and where Lambda functions will be invoked (e.g. `us-east-1`).
 - `execution_role`: ARN of the execution role created at step 3. To find it, go to *Roles* in *IAM* section. Look for the role created before and click on it. The ARN should be at the top of the page (e.g. `arn:aws:iam::1234567890:role/cloudbutton-role`)

- `endpoint`: Endpoint URL of the bucket created at step 11 (e.g. `https://s3.us-east-1.amazonaws.com`)

### Usage

To use AWS Lambda, change the following lines of your local configuration file:
```yaml
    compute_backend : 'aws_lambda'
    storage_backend: 'aws_s3'
```
