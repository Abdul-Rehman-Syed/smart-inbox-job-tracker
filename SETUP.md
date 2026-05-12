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

If you created the local database before migrations were enabled and see an error about `jobstatus` already existing, run this one-time command and start Compose again:

```bash
docker compose run --rm api alembic stamp 0001_create_jobs
docker compose up -d api
```

5. Access:

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/health`
- Database UI: `http://localhost:8081`

Create an account from the app login screen before adding applications. Jobs and stats are scoped to the logged-in user.

Adminer login:

```text
System: PostgreSQL
Server: db
Username: job_tracker
Password: 069358
Database: job_tracker
```

Demo login:

```text
Email: demo@example.com
Password: password123
```

Create or refresh demo data:

```bash
docker compose run --rm api python scripts/seed_demo.py
```

## AWS Deployment Setup

This project is deployed in `us-east-1` with a free-tier-friendly setup:

- Frontend: private S3 bucket `sijt-frontend` behind CloudFront
- Backend: FastAPI Docker container on EC2
- Database: private RDS PostgreSQL
- CI/CD: GitHub Actions builds images, pushes to ECR, deploys through AWS Systems Manager

1. Create an AWS account and enable billing alerts.
2. Create an IAM user for GitHub Actions with least-privilege permissions for ECR, S3, CloudFront invalidations, and SSM deployment support.
3. Create ECR repository `job-tracker-backend`.
4. Create RDS PostgreSQL:
   - Region: `us-east-1`
   - Engine: PostgreSQL
   - Instance class: `db.t4g.micro` or another free-tier eligible micro class
   - Multi-AZ: No
   - Public access: No
   - Backups: 1 to 7 days
   - Security group: allow PostgreSQL only from EC2 security group
5. Create EC2:
   - Ubuntu 24.04
   - Instance class: `t3.micro` or another free-tier eligible micro class
   - Security group: SSH from your IP only, HTTP 80 from anywhere, HTTPS 443 from anywhere
   - Attach an IAM role with `AmazonSSMManagedInstanceCore` and `AmazonEC2ContainerRegistryReadOnly`
   - Install Docker, AWS CLI, and Git
6. Create private S3 bucket `sijt-frontend`.
7. Create CloudFront distribution:
   - Default origin: S3 bucket with Origin Access Control
   - API origin: `ec2-13-221-118-35.compute-1.amazonaws.com` over HTTP port 80
   - Behavior `/api/*`: backend EC2 origin, all HTTP methods, `CachingDisabled`, `AllViewerExceptHostHeader`
   - Default behavior: S3 origin, `CachingOptimized`
   - Custom errors: map 403 and 404 to `/index.html` with status 200
8. Add GitHub secrets listed in `README.md`.
9. Manually run the `Test and Deploy` workflow from the `main` branch.

Current production endpoints:

- Frontend: `https://d2k57hwu6y8pci.cloudfront.net`
- Health check: `https://d2k57hwu6y8pci.cloudfront.net/api/health`

## EC2 Bootstrap Commands

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git unzip
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
```

Install AWS CLI v2 if your Ubuntu package repository does not include `awscli`:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Log out and back in after adding the user to the Docker group. Confirm setup:

```bash
docker --version
aws --version
aws sts get-caller-identity
```

## Migrations

Run migrations locally:

```bash
cd backend
DATABASE_URL="postgresql://user:password@host:5432/job_tracker" alembic upgrade head
```

For production, GitHub Actions runs migrations automatically before restarting the backend container:

```text
docker run --rm ... job-tracker-backend:latest alembic upgrade head
```

## Monitoring

- Use Docker logs or SSM Run Command output for first-pass backend logs.
- Keep `/api/health` wired into CloudFront or uptime checks.
- Add CloudWatch alarms for EC2 CPU, RDS CPU, RDS storage, and 5xx responses.
- Keep RDS backups enabled.

## Git Workflow

- Develop on feature branches.
- Open PRs into `main`.
- Protect `main` with required CI checks.
- Use `develop` for test-only pushes when desired.
