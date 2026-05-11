# Setup Guide

## Local Development Setup

1. Clone the repository and enter the project.
2. Backend with Python 3.11:

```bash
cd backend
cp .env.example .env
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

3. Frontend:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

4. Docker database and backend:

```bash
cd backend
docker compose up --build
```

5. Access:

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/health`
- Database UI: `http://localhost:8081`

Adminer login:

```text
System: PostgreSQL
Server: db
Username: job_tracker
Password: 069358
Database: job_tracker
```

## AWS Deployment Setup

1. Create an AWS account and enable billing alerts.
2. Create an IAM user for GitHub Actions with least-privilege permissions for ECR, S3, CloudFront invalidations, and EC2 deployment support.
3. Create ECR repository `job-tracker-backend`.
4. Create RDS PostgreSQL:
   - Instance class: `db.t3.micro`
   - Multi-AZ: No
   - Public access: No
   - Backups: 7 days
   - Security group: allow PostgreSQL only from EC2 security group
5. Create EC2:
   - Ubuntu 24.04
   - Instance class: `t2.micro`
   - Security group: SSH, HTTP, HTTPS
   - Elastic IP attached
   - Install Docker, Docker Compose plugin, AWS CLI, and Git
6. Create S3 bucket for frontend assets.
7. Create CloudFront distribution pointing to S3 with origin access control.
8. Request ACM certificate for your domain in `us-east-1` for CloudFront.
9. Optional: create an ALB with ACM certificate for backend HTTPS.
10. Add GitHub secrets listed in `README.md`.
11. Push to `main` for first deployment.

## EC2 Bootstrap Commands

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git unzip
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
sudo apt-get install -y awscli
```

Log out and back in after adding the user to the Docker group.

## Migrations

Run migrations locally or on EC2 before first production start:

```bash
cd backend
DATABASE_URL="postgresql://user:password@host:5432/job_tracker" alembic upgrade head
```

For production, you can execute this inside the running backend image:

```bash
docker exec job-tracker-backend alembic upgrade head
```

## Monitoring

- Use CloudWatch agent or Docker logging for backend logs.
- Keep `/api/health` wired into ALB or uptime checks.
- Add CloudWatch alarms for EC2 CPU, RDS CPU, RDS storage, and 5xx responses.
- Keep RDS backups enabled with 7-day retention.

## Git Workflow

- Develop on feature branches.
- Open PRs into `main`.
- Protect `main` with required CI checks.
- Use `develop` for test-only pushes when desired.
