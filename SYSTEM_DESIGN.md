# System Design

## Architecture Overview

```text
User Browser
  -> CloudFront CDN
  -> S3 static React build
  -> FastAPI backend on EC2 through HTTPS
  -> PostgreSQL RDS private subnet/security group
```

GitHub Actions builds and tests both applications. On `main`, it pushes the backend image to ECR, restarts the EC2 Docker container, uploads frontend assets to S3, and invalidates CloudFront.

## Data Flow

1. The React app calls the API client in `frontend/src/services/api.ts`.
2. Users register or log in and receive a signed bearer token.
3. FastAPI validates payloads with Pydantic schemas and resolves the current user from the token.
4. SQLAlchemy writes and reads rows from PostgreSQL, always filtered by `user_id`.
5. Responses are wrapped in `{ success, data, message }`.
6. The frontend refreshes dashboard, table, and charts from `/api/jobs` and `/api/stats`.

## Database Schema

`users`

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| email | varchar(255) | Required, unique |
| full_name | varchar(160) | Optional |
| hashed_password | varchar(255) | PBKDF2 password hash |
| created_at | timestamp | Auto |
| updated_at | timestamp | Auto |

`jobs`

| Column | Type | Notes |
| --- | --- | --- |
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| company | varchar(160) | Required, indexed |
| job_title | varchar(200) | Required |
| job_url | varchar(1000) | Required |
| date_applied | timestamp | Required, indexed |
| status | enum | Applied, Interview, Rejected, Offer |
| salary_min | numeric(12,2) | Optional |
| salary_max | numeric(12,2) | Optional |
| created_at | timestamp | Auto |
| updated_at | timestamp | Auto |

## API Documentation

Auth:

```http
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
```

Create:

```http
POST /api/jobs
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "company": "Acme",
  "job_title": "Frontend Engineer",
  "job_url": "https://example.com/job",
  "date_applied": "2026-05-11T00:00:00Z",
  "status": "Applied",
  "salary_min": 90000,
  "salary_max": 120000
}
```

List and filter:

```http
GET /api/jobs?date_range=30d&status=Interview
```

Stats:

```http
GET /api/stats?date_range=all
```

Health:

```http
GET /api/health
```

## Deployment Architecture

- S3 stores static frontend assets.
- CloudFront serves the frontend over HTTPS and caches assets globally.
- EC2 runs the FastAPI Docker container.
- ECR stores backend Docker images.
- RDS PostgreSQL stores application data.
- Security groups allow database traffic only from EC2.
- ACM provides free TLS certificates for CloudFront and ALB.
- Optional ALB terminates HTTPS before forwarding to EC2.

## Scalability

- Move EC2 to an Auto Scaling Group behind ALB.
- Increase Gunicorn worker count based on CPU and memory.
- Add RDS read replicas when reporting traffic grows.
- Use ElastiCache for high-read dashboards if needed.
- Split CI/CD into blue/green deployments for zero downtime.

## Security

- CORS is configured from `ALLOWED_ORIGINS`.
- Pydantic validates all user input.
- SQLAlchemy parameterization protects against SQL injection.
- React escapes text output by default, reducing XSS risk.
- Secrets live in GitHub Secrets and AWS, not source code.
- RDS should be private and reachable only from EC2.
- HTTPS is used through CloudFront and ALB or a reverse proxy.

The current version includes email/password authentication with signed bearer tokens. Email verification, welcome emails, and Google OAuth are planned follow-ups that require provider credentials and production callback URLs.

## Cost Analysis

Free tier-friendly monthly footprint:

- EC2 `t2.micro` or `t3.micro`: free tier hours for eligible accounts
- RDS `db.t3.micro`: free tier eligible, single-AZ
- S3: minimal static hosting storage
- CloudFront: free tier transfer and requests for typical portfolio traffic
- ECR: small storage footprint for a few Docker images
- ACM: free public certificates

Avoid NAT Gateway, Multi-AZ RDS, large ALBs, and excessive CloudWatch retention if strict free-tier cost control matters.
