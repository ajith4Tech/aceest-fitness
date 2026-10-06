# ACEest Fitness & Gym

A Flask-based fitness and gym management application developed for the **Introduction to DevOps** assignment at BITS Pilani WILP.

The project demonstrates a complete DevOps workflow covering application development, Git version control, automated testing, Docker containerization, GitHub Actions CI, and Jenkins-based BUILD validation.

## Features

- Gym member registration and management
- Member lookup and deletion
- Workout tracking for registered members
- BMI calculation with health categories
- Request and input validation
- REST API endpoints
- Automated Pytest test suite
- Ruff code linting
- Docker containerization
- Non-root Docker execution
- GitHub Actions CI on every push and pull request
- Jenkins automated BUILD and quality validation

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python 3.9 | Application runtime |
| Flask | REST API framework |
| Pytest | Automated testing |
| Ruff | Python linting |
| Docker | Application containerization |
| Jenkins | BUILD and quality gate |
| Git | Version control |
| GitHub | Source code repository |
| GitHub Actions | Continuous Integration |

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

The application exposes REST APIs for basic gym management operations.

The current implementation uses in-memory data storage for members and workouts. This keeps the application simple and focused on the DevOps requirements of the assignment.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Application welcome message |
| GET | `/health` | Application health check |
| GET | `/members` | List all gym members |
| POST | `/members` | Register a new gym member |
| GET | `/members/<id>` | Retrieve a specific member |
| DELETE | `/members/<id>` | Delete a gym member |
| POST | `/bmi` | Calculate BMI and category |
| GET | `/workouts` | List recorded workouts |
| POST | `/workouts` | Add a workout for a registered member |

## Validation

The application validates incoming API requests before processing them.

Examples include:

- Required member name and age
- Age must be between 1 and 120
- Valid member IDs
- Valid workout duration
- Workout must reference an existing member
- Positive weight and height for BMI calculation
- Required request bodies

Invalid requests return appropriate HTTP error responses such as `400` or `404`.

## Local Development

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

The application starts on:

```text
http://localhost:5000
```

## API Examples

### Health Check

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

```bash
curl http://localhost:5000/members
```

Response:

```json
[]
```

### Add a Member

```bash
curl -X POST http://localhost:5000/members \
  -H "Content-Type: application/json" \
  -d '{"name":"John","age":25}'
```

Response:

```json
{
  "id": 1,
  "name": "John",
  "age": 25
}
```

### Get a Member

```bash
curl http://localhost:5000/members/1
```

### Delete a Member

```bash
curl -X DELETE http://localhost:5000/members/1
```

Response:

```json
{
  "message": "Member deleted successfully"
}
```

### Calculate BMI

```bash
curl -X POST http://localhost:5000/bmi \
  -H "Content-Type: application/json" \
  -d '{"weight":70,"height":1.75}'
```

Response:

```json
{
  "bmi": 22.86,
  "category": "Normal weight"
}
```

### Add a Workout

First create a member, then add a workout:

```bash
curl -X POST http://localhost:5000/workouts \
  -H "Content-Type: application/json" \
  -d '{"member_id":1,"exercise":"Running","duration":30}'
```

Response:

```json
{
  "id": 1,
  "member_id": 1,
  "exercise": "Running",
  "duration": 30
}
```

### List Workouts

```bash
curl http://localhost:5000/workouts
```

## Testing

The project uses **Pytest** for automated testing.

The test suite currently contains **18 tests** covering:

- Application welcome endpoint
- Health check
- Empty member list
- Member creation
- Member input validation
- Member age validation
- Member lookup
- Member not found handling
- Member deletion
- BMI calculation
- BMI validation
- BMI category handling
- Workout creation
- Workout validation
- Workout member validation
- Empty workout list

### Run Tests Locally

```bash
python -m pytest -v
```

Expected result:

```text
18 passed
```

## Code Quality

The project uses **Ruff** for Python linting.

Run the linter locally:

```bash
python -m ruff check .
```

A successful run reports:

```text
All checks passed!
```

Python syntax is also checked using:

```bash
python -m py_compile app.py
```

## Docker

Docker is used to package the application together with its Python dependencies and test suite.

### Build the Image

```bash
docker build -t aceest-fitness .
```

### Run the Application

```bash
docker run --rm -p 5000:5000 aceest-fitness
```

The application will be available at:

```text
http://localhost:5000
```

### Run Tests Inside Docker

```bash
docker run --rm aceest-fitness python -m pytest -v
```

Expected result:

```text
18 passed
```

### Docker Security

The application does not run as the Docker `root` user.

The Docker image creates a dedicated `appuser` account and switches to that user before starting the application.

This follows the principle of least privilege and reduces the risk associated with running application processes as root.

## GitHub Actions

GitHub Actions provides automated CI for every **push** and **pull request**.

The workflow is defined in:

```text
.github/workflows/main.yml
```

### CI Pipeline

The workflow performs:

1. Checkout source code
2. Set up Python 3.9
3. Install dependencies
4. Run Ruff linting
5. Check Python syntax
6. Build the Docker image
7. Run the complete Pytest suite inside Docker

### Linting

```bash
python -m ruff check .
```

### Syntax Validation

```bash
python -m py_compile app.py
```

### Docker Image Assembly

```bash
docker build -t aceest-fitness:ci .
```

### Automated Testing

```bash
docker run --rm aceest-fitness:ci python -m pytest -v
```

The GitHub Actions workflow fails automatically if linting, syntax validation, Docker image creation, or automated tests fail.

## Jenkins

Jenkins is used as the primary **BUILD and quality-gate environment**.

The Jenkins Freestyle project:

```text
ACEest-Fitness-Build
```

is configured to pull source code from the GitHub repository and build the `main` branch.

### Jenkins Build Process

Jenkins performs:

1. Pull the latest source code from GitHub
2. Build the Docker image
3. Execute the Pytest test suite inside the Docker container
4. Mark the BUILD successful only when all stages pass

### Docker Build

```bash
docker build --no-cache -t aceest-fitness:jenkins .
```

### Test Execution

```bash
docker run --rm aceest-fitness:jenkins python -m pytest -v
```

### Automated Jenkins Trigger

Jenkins uses **SCM polling** to automatically detect changes in the GitHub repository.

The configured polling schedule is:

```text
H/5 * * * *
```

When a change is detected on `main`, Jenkins automatically starts a new BUILD without requiring a manual **Build Now** action.

## Git Workflow

Git is used for version control and GitHub is used as the remote repository.

The project uses feature branches for development before merging changes into `main`.

Example workflow:

```text
main
  |
  +-- feature/fitness-api-enhancements
              |
              +-- Pull Request
                      |
                      +-- GitHub Actions
                      |
                      +-- Merge
                            |
                            v
                           main
```

The project uses meaningful commit messages for application, testing, CI, Docker, and documentation changes.

## CI/CD Workflow

The overall workflow is:

```text
Developer
    |
    | Push / Pull Request
    v
GitHub
    |
    +---------------------------+
    |                           |
    v                           v
GitHub Actions              Jenkins
    |                           |
    |                           | SCM Polling
    |                           |
    v                           v
Lint + Syntax             Docker Build
    |                           |
Docker Build                    v
    |                        Pytest
    v                           |
Pytest                          v
    |                       BUILD SUCCESS
    v
PASS
```

GitHub Actions provides continuous integration for repository changes, while Jenkins provides the primary Docker-based BUILD and quality gate.

## DevOps Practices Demonstrated

This project demonstrates the following DevOps practices:

- **Version Control** — Git and GitHub
- **Branch-based Development** — Feature branch and Pull Request workflow
- **Automated Testing** — 18 Pytest test cases
- **Code Quality** — Ruff linting and Python syntax validation
- **Containerization** — Docker
- **Container Security** — Non-root application user
- **Continuous Integration** — GitHub Actions
- **Automated BUILD Validation** — Jenkins
- **Automated Jenkins Triggering** — SCM polling
- **Reproducible Testing** — Tests executed inside Docker

## Assignment Requirements

| Requirement | Implementation |
|-------------|----------------|
| Flask application | `app.py` |
| Git version control | Git |
| Public remote repository | GitHub |
| Meaningful commits | Git commit history |
| Branch management | Feature branch + Pull Request |
| Automated testing | Pytest |
| Test coverage | 18 automated tests |
| Code linting | Ruff |
| Docker containerization | `Dockerfile` |
| Docker-based testing | Pytest executed inside Docker |
| Docker security | Non-root `appuser` |
| Jenkins BUILD | Jenkins Freestyle Project |
| Jenkins automation | SCM polling |
| GitHub Actions | `.github/workflows/main.yml` |
| Build and syntax validation | Ruff + `py_compile` |
| Docker image assembly | Docker build in GitHub Actions |
| Automated CI testing | Pytest inside Docker |
| Documentation | `README.md` |

## Repository

GitHub:

https://github.com/ajith4Tech/aceest-fitness

## Conclusion

ACEest Fitness & Gym demonstrates a complete DevOps workflow from application development and version control through automated testing, code quality checks, containerization, GitHub Actions CI, and Jenkins BUILD validation.

The project uses a feature-branch workflow, automated Pull Request validation, Docker-based testing, non-root container execution, and automated Jenkins builds to provide a consistent and repeatable development and delivery process.
