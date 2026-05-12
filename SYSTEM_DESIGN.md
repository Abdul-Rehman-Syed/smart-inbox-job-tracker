# System Design

## Architecture Overview

```text
User Browser
  -> CloudFront CDN
     -> Default behavior (*) -> private S3 bucket with React static build
     -> /api/* behavior      -> FastAPI Docker container on EC2 over HTTP port 80
  -> PostgreSQL RDS protected by security group
```

GitHub Actions builds and tests both applications. Manual production deployment from `main` pushes the backend image to ECR, asks AWS Systems Manager to run deployment commands on EC2, uploads frontend assets to S3, and invalidates CloudFront.

Production URL:

```text
https://d2k57hwu6y8pci.cloudfront.net
```

## Data Flow

1. CloudFront serves the React app from S3.
2. The React app calls the API client in `frontend/src/services/api.ts`.
3. In production, `VITE_API_BASE_URL=/api`, so API requests go back through CloudFront.
4. CloudFront forwards `/api/*` requests to the EC2 backend origin.
5. Users register or log in and receive a signed bearer token.
6. FastAPI validates payloads with Pydantic schemas and resolves the current user from the token.
7. SQLAlchemy writes and reads rows from PostgreSQL, always filtered by `user_id`.
8. Responses are wrapped in `{ success, data, message }`.
9. The frontend refreshes dashboard, table, and charts from `/api/jobs` and `/api/stats`.

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
- CloudFront serves the frontend over HTTPS and caches static assets globally.
- CloudFront forwards `/api/*` to the EC2 backend origin with caching disabled.
- EC2 runs the FastAPI Docker container on host port 80 mapped to container port 8000.
- ECR stores backend Docker images.
- RDS PostgreSQL stores application data.
- Security groups allow database traffic only from EC2.
- Systems Manager Run Command lets GitHub Actions deploy without opening SSH to GitHub.

Current AWS resources:

| Layer | Resource |
| --- | --- |
| Frontend CDN | CloudFront `d2k57hwu6y8pci.cloudfront.net` |
| Frontend storage | S3 bucket `sijt-frontend` |
| Backend compute | EC2 instance `job-tracker-backend` |
| Backend image registry | ECR repository `job-tracker-backend` |
| Database | RDS PostgreSQL `job-tracker-db` |
| Deployment control | AWS Systems Manager Run Command |

## Scalability

- Move EC2 to an Auto Scaling Group behind ALB.
- Replace EC2 Docker deployment with ECS/Fargate when traffic or operational needs grow.
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
- HTTPS is used for browser traffic through CloudFront.
- SSH is not required for CI/CD. Deployment uses SSM Run Command.
- S3 remains private and readable by CloudFront through Origin Access Control.

The current version includes email/password authentication with signed bearer tokens. Email verification, welcome emails, and Google OAuth are planned follow-ups that require provider credentials and production callback URLs.

## Cost Analysis

Free tier-friendly monthly footprint:

- EC2 `t3.micro`: free tier eligible for this deployment
- RDS `db.t4g.micro`: free tier eligible, single-AZ
- S3: minimal static hosting storage
- CloudFront: free tier transfer and requests for typical portfolio traffic
- ECR: small storage footprint for a few Docker images
- ACM: free public certificates when a custom domain is added later

Avoid NAT Gateway, Multi-AZ RDS, AWS WAF, large ALBs, and excessive CloudWatch retention if strict free-tier cost control matters.
