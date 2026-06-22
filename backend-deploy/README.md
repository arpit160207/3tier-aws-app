# 3-Tier AWS App Backend

This repository contains the backend API for a 3-tier AWS application, implemented with Flask and deployed using Elastic Beanstalk.

## Project Structure

- `application.py` - Flask application with authentication, registration, login, and dashboard endpoints.
- `requirements.txt` - Python dependencies.
- `Procfile` - Gunicorn startup command for Elastic Beanstalk.
- `bucket-policy.json` - S3 bucket policy (deployment/resource configuration).
- `.ebextensions/`, `.elasticbeanstalk/` - Elastic Beanstalk configuration files.

## Features

- Register users with hashed passwords using `werkzeug.security`
- Login with email/password authentication
- JWT token generation and validation using `PyJWT`
- MongoDB connection via `pymongo`
- CORS support for cross-origin requests
- Health check endpoint for Elastic Beanstalk

## Requirements

- Python 3.11+ (recommended)
- MongoDB Atlas or a MongoDB database accessible via URI
- Git
- AWS Elastic Beanstalk CLI (for deployment)

## Installation

1. Create a virtual environment:

   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

The application reads configuration from environment variables:

- `MONGO_URI` - MongoDB connection string. Default: `mongodb://localhost:27017/myapp`
- `SECRET_KEY` - JWT signing secret. Default: `dev-secret-key-change-in-prod`
- `APP_ENV` - Optional environment label, used in dashboard output.

## Running Locally

```bash
python application.py
```

The backend will run on `http://0.0.0.0:5000`.

## Elastic Beanstalk Deployment

The `Procfile` starts the app with Gunicorn:

```text
web: gunicorn --bind 0.0.0.0:8000 --workers 3 application:application
```

Deploy using Elastic Beanstalk CLI or AWS Console and ensure the required environment variables are configured in the EB environment.

## API Endpoints

### GET /
Health/status check returning basic app state.

### GET /health
Elastic Beanstalk health check endpoint.

### POST /api/register
Register a new user.

Request body example:

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword"
}
```

### POST /api/login
Authenticate an existing user.

Request body example:

```json
{
  "email": "jane@example.com",
  "password": "securepassword"
}
```

### GET /api/dashboard
Protected endpoint requiring `Authorization: Bearer <token>`.

Returns user dashboard statistics and environment details.

## Notes

- Change `SECRET_KEY` in production to a strong secret.
- Use a secure MongoDB connection string for production deployment.
- Ensure the AWS Elastic Beanstalk environment uses the correct Python platform and has network access to MongoDB.
