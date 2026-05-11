# Smart Inbox Job Tracker

A production-ready portfolio job application tracker built with React, TypeScript, FastAPI, PostgreSQL, Docker, and AWS free-tier-friendly deployment. The app now supports user accounts so each person only sees their own applications.

## Features

- Add, edit, delete, and track job applications
- Status workflow: Applied, Interview, Rejected, Offer
- Dashboard statistics for totals, interviews, rejections, and pending applications
- Pie chart by status and bar chart for top companies
- Date range and status filters
- Email/password authentication with bearer tokens
- User-owned job applications and dashboard statistics
- Fully typed React API client
- FastAPI response envelope and validation
- Dockerized local and production workflows
- GitHub Actions test and deployment pipeline

## Tech Stack

- Frontend: React 18, TypeScript, Recharts, Axios, Vite, Jest, React Testing Library
- Backend: Python 3.11, FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, pytest
- Database: PostgreSQL on AWS RDS
- Deployment: S3, CloudFront, EC2, ECR, RDS, ACM, optional ALB

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
- `GET /api/health`

Job and stats endpoints require:

```http
Authorization: Bearer <access_token>
```

## Deployment

The included GitHub Actions workflow runs tests on `develop` and deploys on `main`. Configure these secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REGISTRY`
- `EC2_HOST`
- `EC2_USER`
- `EC2_KEY`
- `DATABASE_URL`
- `SECRET_KEY`
- `API_BASE_URL`
- `API_ALLOWED_ORIGINS`
- `S3_BUCKET`
- `CLOUDFRONT_DISTRIBUTION_ID`

See [SETUP.md](SETUP.md) for the complete AWS setup checklist and [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for architecture details.

## Screenshots

Add screenshots or a short demo GIF after the first deployment.

## Contributing

Use feature branches, open pull requests into `main`, and keep tests passing. Protect `main` in GitHub so changes require a PR review and passing CI checks.

## License

MIT
