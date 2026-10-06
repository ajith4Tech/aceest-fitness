# ACEest Fitness & Gym

A Flask-based fitness and gym management application developed as part of the Introduction to DevOps assignment.

This project demonstrates a complete DevOps workflow using Git, GitHub, Pytest, Docker, Jenkins, and GitHub Actions.

## Features

- Fitness and gym application health check
- Gym member registration
- Member listing
- BMI calculation
- Input validation
- Automated unit testing
- Docker containerization
- Jenkins build validation
- GitHub Actions CI pipeline

## Technology Stack

- Python 3.9
- Flask
- Pytest
- Docker
- Jenkins
- Git
- GitHub
- GitHub Actions

## Project Structure

```text
aceest-fitness/
├── .github/
│   └── workflows/
│       └── main.yml
├── tests/
│   └── test_app.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── app.py
└── requirements.txt
```

## Application

The application provides basic fitness and gym management functionality through REST API endpoints.

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Application welcome message |
| GET | `/health` | Application health check |
| GET | `/members` | List all gym members |
| POST | `/members` | Add a new gym member |
| POST | `/bmi` | Calculate BMI |

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ajith4Tech/aceest-fitness.git
cd aceest-fitness
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will start on:

```text
http://localhost:5000
```

## API Usage

### Health Check

Request:

```bash
curl http://localhost:5000/health
```

Response:

```json
{
  "status": "healthy"
}
```

### List Members

Request:

```bash
curl http://localhost:5000/members
```

Example response:

```json
[]
```

### Add a Member

Request:

```bash
curl -X POST http://localhost:5000/members \
  -H "Content-Type: application/json" \
  -d '{"name":"John","age":25}'
```

Example response:

```json
{
  "id": 1,
  "name": "John",
  "age": 25
}
```

### Calculate BMI

Request:

```bash
curl -X POST http://localhost:5000/bmi \
  -H "Content-Type: application/json" \
  -d '{"weight":70,"height":1.75}'
```

Example response:

```json
{
  "bmi": 22.86
}
```

## Unit Testing

The project uses Pytest for automated unit testing.

The test suite covers:

- Home endpoint
- Health endpoint
- Member listing
- Member creation
- Invalid member input
- BMI calculation
- Invalid BMI input

### Run Tests Locally

From the project root:

```bash
python -m pytest -v
```

Expected result:

```text
7 passed
```

## Docker

The Flask application is containerized using Docker to provide a consistent execution environment.

### Build the Docker Image

```bash
docker build -t aceest-fitness .
```

### Run the Docker Container

```bash
docker run --rm -p 5000:5000 aceest-fitness
```

The application will be available at:

```text
http://localhost:5000
```

### Run Tests Inside the Docker Container

The test suite can also be executed inside the container:

```bash
docker run --rm aceest-fitness python -m pytest -v
```

Expected result:

```text
7 passed
```

## Jenkins Integration

Jenkins is used as the primary BUILD and quality-gate environment.

The Jenkins job is configured to:

1. Pull the latest source code from the GitHub repository.
2. Check out the `main` branch.
3. Build the Docker image.
4. Run the Pytest test suite inside the Docker container.
5. Mark the build as successful only when the Docker build and tests pass.

### Jenkins Docker Build

The Jenkins build uses:

```bash
docker build --no-cache -t aceest-fitness:jenkins .
```

### Jenkins Test Execution

Tests are executed inside the Docker image using:

```bash
docker run --rm aceest-fitness:jenkins python -m pytest -v
```

If the Docker build or test execution fails, Jenkins marks the build as failed.

## GitHub Actions

GitHub Actions provides automated CI for every push and pull request.

The workflow is defined in:

```text
.github/workflows/main.yml
```

### GitHub Actions Pipeline

The workflow performs the following stages:

1. Checkout source code
2. Set up Python
3. Install application dependencies
4. Perform Python syntax validation
5. Build the Docker image
6. Run the Pytest suite inside the Docker container

### Build and Syntax Validation

Python syntax is checked using:

```bash
python -m py_compile app.py
```

### Docker Image Assembly

The Docker image is built using:

```bash
docker build -t aceest-fitness:ci .
```

### Automated Testing

Tests are executed inside the Docker container using:

```bash
docker run --rm aceest-fitness:ci python -m pytest -v
```

The workflow fails automatically if the application has syntax errors, the Docker image cannot be built, or any automated test fails.

## CI/CD Workflow

The overall DevOps workflow implemented in this project is:

```text
Developer
    |
    | Git Push / Pull Request
    v
GitHub
    |
    +-----------------------------+
    |                             |
    v                             v
Jenkins                     GitHub Actions
    |                             |
Docker Build                 Build & Lint
    |                             |
Pytest                      Docker Build
    |                             |
    v                             v
BUILD SUCCESS               Pytest
                                  |
                                  v
                                PASS
```

## Version Control

Git is used for source code version control and GitHub is used as the remote repository.

The project follows meaningful commit messages for major changes, including:

- Initial application implementation
- Docker configuration
- GitHub Actions CI workflow
- Project documentation

## Repository

GitHub Repository:

https://github.com/ajith4Tech/aceest-fitness

## Assignment Requirements Covered

| Requirement | Implementation |
|-------------|----------------|
| Flask application | `app.py` |
| Version control | Git |
| Remote repository | GitHub |
| Unit testing | Pytest |
| Containerization | Docker |
| Jenkins BUILD | Jenkins Freestyle Project |
| Docker-based testing | Pytest executed inside Docker |
| CI pipeline | GitHub Actions |
| Build and lint | Python syntax validation |
| Docker image assembly | GitHub Actions Docker build |
| Automated testing | Pytest inside Docker |
| Documentation | `README.md` |

## Conclusion

This project demonstrates the complete application lifecycle from local development and version control through automated testing, containerization, Jenkins-based BUILD validation, and GitHub Actions continuous integration.
