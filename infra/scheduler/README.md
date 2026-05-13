# AWS Start/Stop Scheduler

This Lambda function is used to reduce portfolio demo costs by starting and stopping the EC2 backend and RDS database on a schedule.

Current schedule:

- Start: 08:00 Europe/Berlin
- Stop: 23:00 Europe/Berlin

Target resources:

- EC2 instance: `i-0888c605093ee3f83`
- RDS instance: `job-tracker-db`

## Lambda Environment Variables

```text
EC2_INSTANCE_ID=i-0888c605093ee3f83
RDS_INSTANCE_ID=job-tracker-db
```

## Lambda Test Events

Start:

```json
{
  "action": "start"
}
```

Stop:

```json
{
  "action": "stop"
}
```

## IAM Policy For Lambda Role

Attach this policy to the Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds:StartDBInstance",
        "rds:StopDBInstance",
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

The default Lambda basic execution role is also needed so logs can be written to CloudWatch.

## EventBridge Scheduler Payloads

Create two EventBridge Scheduler schedules in `us-east-1`.

Start schedule:

- Time: `08:00`
- Timezone: `Europe/Berlin`
- Target: Lambda function
- Payload:

```json
{
  "action": "start"
}
```

Stop schedule:

- Time: `23:00`
- Timezone: `Europe/Berlin`
- Target: Lambda function
- Payload:

```json
{
  "action": "stop"
}
```
