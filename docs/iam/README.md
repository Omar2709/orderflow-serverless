# IAM

## CreateOrderExecutionRole

`CreateOrderExecutionRole` is the execution role used by `CreateOrderLambda`.

### Trusted principal

- AWS Lambda (`lambda.amazonaws.com`)

The trust policy allows the AWS Lambda service to assume this role through `sts:AssumeRole`.

### Current permissions

The Lambda function currently only needs permission to write logs to Amazon CloudWatch Logs.

These permissions will be provided by the AWS managed policy:

`AWSLambdaBasicExecutionRole`

The relevant CloudWatch Logs actions are:

- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

### Permissions not currently required

`CreateOrderLambda` does not currently require access to:

- DynamoDB
- SQS
- SNS
- Secrets Manager

These permissions must not be added until the application has a concrete requirement for them.

## Future permissions

When persistence is introduced, `CreateOrderExecutionRole` may require access to DynamoDB.

Those permissions should follow the principle of least privilege by restricting both the allowed actions and the resources they can operate on.

For example, if the application only needs to create and retrieve orders, the role should receive only the necessary DynamoDB actions, such as `dynamodb:PutItem` and `dynamodb:GetItem`, scoped to the specific OrderFlow table instead of using broad permissions such as `dynamodb:*` on `*`.