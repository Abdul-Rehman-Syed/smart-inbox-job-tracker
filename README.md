# Smart Inbox Job Tracker

A production-ready portfolio job application tracker built with React, TypeScript, FastAPI, PostgreSQL, Docker, and AWS free-tier-friendly deployment. The app now supports user accounts so each person only sees their own applications.

## Demo

Production app:

```text
https://d2k57hwu6y8pci.cloudfront.net
```

Production health check:

```text
https://d2k57hwu6y8pci.cloudfront.net/api/health
```

Local app:

```text
http://localhost:3000
```

Demo account:

```text
Email: demo@example.com
Password: password123
```

Seed or refresh local demo data:

```bash
cd backend
docker compose run --rm api python scripts/seed_demo.py
```

The seed script only replaces jobs for the demo user.

Seed or refresh production demo data:

```text
GitHub Actions -> Seed Demo Data -> Run workflow -> main
```

The production seed workflow runs the same script through AWS Systems Manager and the deployed backend image.

## Features

- Add, edit, delete, and track job applications
- Status workflow: Applied, Interview, Rejected, Offer
- Dashboard statistics for totals, interviews, rejections, and pending applications
- Pie chart by status and bar chart for top companies
- Date range and status filters
- Expandable status history for each job application
- Gmail automation interface and backend foundation for future inbox sync
- Email/password authentication with bearer tokens
- User-owned job applications and dashboard statistics
- Fully typed React API client
- FastAPI response envelope and validation
- Dockerized local and production workflows
- GitHub Actions test and automatic deployment pipeline
- AWS Lambda and EventBridge Scheduler cost-control automation

## What This Demonstrates

- Full-stack CRUD with a React TypeScript frontend and FastAPI backend
- Authenticated, user-owned data with JWT bearer tokens
- PostgreSQL persistence through Docker Compose locally and AWS RDS in production
- Dashboard statistics and charts from backend aggregation
- Production-style Dockerfiles for frontend and backend
- CI checks for backend formatting/lint/tests and frontend lint/tests/build
- AWS deployment with S3, CloudFront, EC2, ECR, RDS, Lambda, EventBridge, and Systems Manager

## Tech Stack

- Frontend: React 18, TypeScript, Recharts, Axios, Vite, Jest, React Testing Library
- Backend: Python 3.11, FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, pytest
- Database: PostgreSQL on AWS RDS
- Deployment: S3 private bucket, CloudFront, EC2, ECR, RDS, AWS Systems Manager, Lambda, EventBridge Scheduler

## Local Setup

Backend:

```bash
cd backend
cp .env.example .env
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Docker:

```bash
cd backend
docker compose up --build
```

Open the frontend at `http://localhost:3000` and the API docs at `http://localhost:8000/docs`.

Database UI:

```text
http://localhost:8081
```

Adminer login:

```text
System: PostgreSQL
Server: db
Username: job_tracker
Password: 069358
Database: job_tracker
```

## Tests

```bash
cd backend
pytest --cov=app --cov=main --cov-report=term-missing
```

```bash
cd frontend
npm test
```

## API

All API responses use:

```json
{
  "success": true,
  "data": {},
  "message": "optional message"
}
```

Endpoints:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/jobs`
- `GET /api/jobs?date_range=all|7d|30d&status=Applied`
- `GET /api/jobs/{job_id}`
- `PUT /api/jobs/{job_id}`
- `DELETE /api/jobs/{job_id}`
- `GET /api/stats?date_range=all|7d|30d`
- `GET /api/email/gmail/status`
- `POST /api/email/gmail/disconnect`
- `POST /api/email/sync`
- `GET /api/email/events`
- `GET /api/health`

Job and stats endpoints require:

```http
Authorization: Bearer <access_token>
```

## Deployment

The included GitHub Actions workflow runs tests on pushes and pull requests. Pushes to `main` automatically deploy after backend and frontend checks pass. Manual `workflow_dispatch` remains available as a backup deployment button.

Current production architecture:

- CloudFront serves the React frontend from private S3 bucket `sijt-frontend`.
- CloudFront forwards `/api/*` requests to the EC2 backend origin.
- EC2 runs the FastAPI Docker container and pulls images from ECR.
- GitHub Actions deploys to EC2 through AWS Systems Manager Run Command, not public SSH.
- RDS PostgreSQL stores persistent user and job data.
- AWS Lambda and EventBridge Scheduler start the EC2/RDS stack at 08:00 and stop it at 23:00 Europe/Berlin to reduce running costs.

Production URL:

```text
https://d2k57hwu6y8pci.cloudfront.net
```

Required GitHub Actions secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REGISTRY`
- `EC2_INSTANCE_ID`
- `DATABASE_URL`
- `SECRET_KEY`
- `API_ALLOWED_ORIGINS`
- `S3_BUCKET`
- `CLOUDFRONT_DISTRIBUTION_ID`

Recommended `API_ALLOWED_ORIGINS` value for local plus deployed frontend:

```text
http://localhost:3000,https://d2k57hwu6y8pci.cloudfront.net
```

See [SETUP.md](SETUP.md) for the complete AWS setup checklist and [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for architecture details.

## Roadmap

- Email welcome/verification through AWS SES or another email provider
- Google OAuth login
- Gmail inbox sync for application updates, planned in [Email Automation Design](docs/EMAIL_AUTOMATION_DESIGN.md)
- Demo screenshots and hosted portfolio walkthrough

## Screenshots

Add these screenshots before or after the first deployment:

```text
docs/screenshots/login.png
docs/screenshots/dashboard.png
docs/screenshots/job-table.png
```

Suggested capture list:

- Login/register screen
- Dashboard with seeded demo account
- Job table with status filters and scrolling list
- Charts section

Then embed them here:

```md
![Login screen](docs/screenshots/login.png)
![Dashboard](docs/screenshots/dashboard.png)
![Job table](docs/screenshots/job-table.png)
```

## Contributing

Use feature branches, open pull requests into `main`, and keep tests passing. Protect `main` in GitHub so changes require a PR review and passing CI checks.

## License

MIT
