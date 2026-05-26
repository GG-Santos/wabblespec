# Framework-Specific Architecture: Serverless (AWS Lambda / Cloud Functions)

> **Applies when:** `serverless.yml`, `sam.yaml`, `template.yaml`, or function deployment config detected.
> Covers AWS Lambda (primary) with notes for GCP Cloud Functions and Azure Functions.
> **Version authority:** AWS Lambda runtime: Node.js 20.x or Python 3.12. SAM CLI 1.x. Serverless Framework 3.x.

---

## Provider and Runtime Declaration [REQUIRED]

| Decision | Options |
|---|---|
| **Cloud provider** | AWS / GCP / Azure / Cloudflare Workers |
| **Runtime** | Node.js 20 / Python 3.12 / Go 1.21 / Java 21 |
| **Deployment framework** | AWS SAM / Serverless Framework / CDK / Pulumi / Terraform |
| **Trigger types** | API Gateway / SQS / SNS / S3 / EventBridge / Schedule |

**Declared configuration:** ___

---

## Handler Pattern

```typescript
// AWS Lambda — Node.js (TypeScript)
import { APIGatewayProxyEventV2, APIGatewayProxyResultV2, Context } from 'aws-lambda'

// Handler signature — never use any; type the event shape explicitly
export const handler = async (
  event: APIGatewayProxyEventV2,
  context: Context
): Promise<APIGatewayProxyResultV2> => {
  // context.callbackWaitsForEmptyEventLoop = false  // only if using async resources outside handler scope

  try {
    const body = event.body ? JSON.parse(event.body) : null
    if (!body?.name) {
      return { statusCode: 400, body: JSON.stringify({ error: 'name is required' }) }
    }
    const result = await processRequest(body)
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result)
    }
  } catch (err) {
    console.error('Unhandled error:', err)  // CloudWatch logs
    return { statusCode: 500, body: JSON.stringify({ error: 'Internal server error' }) }
  }
}
```

```python
# AWS Lambda — Python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event: dict, context) -> dict:
    try:
        body = json.loads(event.get('body') or '{}')
        if not body.get('name'):
            return {'statusCode': 400, 'body': json.dumps({'error': 'name is required'})}
        result = process_request(body)
        return {'statusCode': 200, 'body': json.dumps(result)}
    except Exception as e:
        logger.exception('Unhandled error')
        return {'statusCode': 500, 'body': json.dumps({'error': 'Internal server error'})}
```

---

## Cold Start Optimization

Cold starts occur when Lambda initializes a new execution environment. Minimizing cold start time is mandatory for latency-sensitive functions.

**What happens during a cold start:**
1. Lambda provisions a new container
2. Downloads and extracts the function deployment package
3. Initializes the runtime
4. Runs module-level code (imports, global variable initialization)
5. Calls the handler

**Cold start mitigation:**

```typescript
// OUTSIDE the handler — runs once per execution environment, not per invocation
// Safe: db clients, config loading, SDK clients (reuse across invocations)
// Unsafe: per-request state, anything that must be fresh each call

import { DynamoDBClient } from '@aws-sdk/client-dynamodb'
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm'

// Initialize client once — reused across warm invocations
const ddb = new DynamoDBClient({ region: process.env.AWS_REGION })

// Lazy-load config on first invocation — avoids cold start cost if unused
let config: AppConfig | null = null
async function getConfig(): Promise<AppConfig> {
  if (config) return config
  const ssm = new SSMClient({ region: process.env.AWS_REGION })
  const param = await ssm.send(new GetParameterCommand({
    Name: process.env.CONFIG_PARAM_NAME!,
    WithDecryption: true
  }))
  config = JSON.parse(param.Parameter!.Value!)
  return config
}

export const handler = async (event: APIGatewayProxyEventV2) => {
  const cfg = await getConfig()  // cached after first call
  // ...
}
```

**Bundle size:** Cold start time scales with bundle size. Every MB of dependencies adds ~10ms of cold start. Tree-shake aggressively. Import only what you use from AWS SDKs.

```typescript
// BAD — imports entire SDK
import AWS from 'aws-sdk'

// GOOD — imports only DynamoDB client (~200KB vs ~3MB)
import { DynamoDBClient, GetItemCommand } from '@aws-sdk/client-dynamodb'
```

---

## Event Shape Reference

Different triggers pass different event shapes. Always type the event parameter correctly.

```typescript
// API Gateway HTTP API (v2) — preferred over REST API (v1)
import { APIGatewayProxyEventV2 } from 'aws-lambda'
const pathParam = event.pathParameters?.id
const queryParam = event.queryStringParameters?.page
const body = event.body  // string | null — parse manually

// SQS trigger — may receive multiple records per invocation
import { SQSEvent, SQSRecord } from 'aws-lambda'
for (const record of event.Records) {
  const message = JSON.parse(record.body)
  // If processing fails for some records, return { batchItemFailures: [...] }
  // for partial batch failure support — do not throw (fails entire batch)
}

// S3 trigger
import { S3Event } from 'aws-lambda'
for (const record of event.Records) {
  const bucket = record.s3.bucket.name
  const key = decodeURIComponent(record.s3.object.key.replace(/\+/g, ' '))
}

// EventBridge scheduled event
import { EventBridgeEvent } from 'aws-lambda'
// event['detail-type'], event.source, event.detail
```

---

## Lambda Limits — Declare Compliance

| Limit | Value | Design implication |
|---|---|---|
| Max execution time | 15 minutes | Tasks longer than 15 min → Step Functions or ECS |
| Memory | 128 MB – 10 GB | Memory also scales CPU — declare required memory |
| Payload size (sync) | 6 MB request + 6 MB response | Large files → S3 presigned URL pattern |
| Payload size (async) | 256 KB | SQS message body limit is also 256 KB |
| Concurrency (default) | 1000 per region | Declare reserved concurrency if burst isolation needed |
| Ephemeral storage `/tmp` | 512 MB – 10 GB | Declare if used; not shared across invocations |
| Layers | Max 5 layers | Dependencies in a layer require explicit size budgeting |

**Declare for this service:**
- Expected memory: ___
- Expected duration (p99): ___
- Reserved concurrency: ___
- `/tmp` usage: ___

---

## Environment Variables and Secrets

```typescript
// Never hardcode secrets — use environment variables referencing SSM/Secrets Manager
// In SAM template:
// Parameters:
//   DbPassword:
//     Type: AWS::SSM::Parameter::Value<String>
//     Default: /myapp/prod/db-password

// In handler — read from env at startup
const DB_HOST = process.env.DB_HOST!       // fails fast if missing
const DB_PASSWORD = process.env.DB_PASSWORD! // resolved from SSM at deploy time

// For dynamic secret rotation — fetch from Secrets Manager at invocation time
// (not at cold start — rotation won't be picked up until next cold start otherwise)
```

**Forbidden:** Secrets in function code, in `serverless.yml` environment section as plaintext, or in CloudFormation parameters as Default values.

---

## GWT Acceptance Scenarios

```
Given: a Lambda function receives an API Gateway request with a missing required field
When: the handler validates the event body
Then: the function returns statusCode 400 with an error message
      AND the function does not call any downstream service
      AND the invocation is logged (CloudWatch) with the validation failure

Given: a Lambda is invoked for the first time (cold start)
When: the execution environment initializes
Then: SDK clients are initialized at module level (not inside the handler)
      AND config parameters are loaded lazily (first invocation only)
      AND the cold start duration meets the declared p99 target

Given: an SQS-triggered function fails to process one message out of a batch of 10
When: the handler encounters an error on the failing record
Then: the handler returns a batchItemFailures response (not a thrown exception)
      AND only the failing message is returned to the queue for retry
      AND the 9 successful messages are not reprocessed
```
