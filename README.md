# ACEest Fitness & Gym — CI/CD Pipeline

A Flask REST API for a fitness and gym management system, delivered through a fully automated
CI/CD pipeline: **GitHub → Jenkins → Pytest → SonarQube → Docker Hub → Kubernetes**, with five
deployment strategies and automatic rollback.

Developed for the **Introduction to DevOps** course (Assignment 2), BITS Pilani WILP.

## Technology Stack

| Area | Tool |
|------|------|
| Application | Python 3.12, Flask |
| Version control | Git, GitHub (feature branches, pull requests, release tags) |
| CI/CD server | Jenkins (declarative pipeline, SCM polling) |
| Testing | Pytest, pytest-cov (also run inside the container) |
| Linting | Ruff |
| Code quality | SonarQube (static analysis + quality gate) |
| Containerization | Docker |
| Registry | Docker Hub — [`ajith0b1m/aceest-fitness`](https://hub.docker.com/r/ajith0b1m/aceest-fitness) |
| Orchestration | Kubernetes (Minikube) with NGINX Ingress |
| Additional CI | GitHub Actions (lint, test, build on every push and PR) |

## Application Versions

Each version is a Git tag and a Docker Hub image tag.

| Version | Feature | Ported from |
|---------|---------|-------------|
| 1.0.0 | Members, workouts, BMI calculator, health and version endpoints | — |
| 1.1.0 | Training programs: Fat Loss, Muscle Gain, Beginner | `Aceestver-1.0` |
| 1.2.0 | Daily calorie estimate per program (weight × program factor) | `Aceestver-1.1` |
| 2.0.0 | Weekly progress tracking with average adherence | `Aceestver2.0.1` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check (used by Kubernetes probes) |
| GET | `/version` | Running application version |
| GET / POST | `/members` | List / register members |
| GET / DELETE | `/members/<id>` | Get / delete a member |
| POST | `/bmi` | Calculate BMI and category |
| GET / POST | `/workouts` | List / log workouts |
| GET | `/programs` | List training programs |
| GET | `/programs/<code>` | Program details (workout, diet, calories) |
| GET | `/programs/<code>/calories?weight=70` | Daily calorie estimate |
| GET / POST | `/members/<id>/progress` | Weekly adherence log and summary |

Data is stored in memory, so each pod has its own data. This keeps the focus on the DevOps
pipeline; a shared database would be the next step for a production setup.

## Project Structure

```text
aceest-fitness/
├── ACEest_Fitness.py              # Flask application
├── tests/test_app.py              # Pytest test suite
├── requirements.txt
├── Dockerfile
├── Jenkinsfile                    # Jenkins CI/CD pipeline
├── sonar-project.properties       # SonarQube configuration
├── .github/workflows/main.yml     # GitHub Actions CI
└── k8s/
    ├── rolling-update/            # Deployment + NodePort service
    ├── blue-green/                # Blue and green deployments, live + preview services
    ├── progressive/               # Stable, new and shadow backends
    ├── canary/                    # Weighted canary ingress
    ├── ab-testing/                # Header-based A/B ingress
    ├── shadow/                    # Traffic-mirroring ingress
    └── scripts/                   # Deploy, verify and rollback script per strategy
```

## CI/CD Pipeline

Jenkins polls GitHub every 2 minutes and runs on every change to `main`:

1. **Install** dependencies in a virtual environment
2. **Lint** with Ruff
3. **Unit Tests** with Pytest, coverage and JUnit reports
4. **SonarQube Analysis**
5. **Quality Gate**: the pipeline stops if the gate fails
6. **Docker Build**, tagged with the version and build number
7. **Test in Container**: Pytest runs inside the built image
8. **Push to Docker Hub**: version tag and `latest`
9. **Deploy** using the selected strategy, with automatic verification and rollback

A broken build never reaches Docker Hub or the cluster. Test reports and coverage are archived
as build artifacts.

## Deployment Strategies

Choose the strategy in Jenkins with **Build with Parameters → STRATEGY**. Polling builds use
`rolling`.

| Strategy | How it works | Rollback | Access |
|----------|--------------|----------|--------|
| Rolling update | Pods replaced one at a time (`maxUnavailable: 0`, readiness probes) | `kubectl rollout undo`, automatic on failure | `:30080` |
| Blue-green | New version deployed to the idle colour, tested on the preview service, then traffic switched in one step | Switch the service back to the previous colour | `:30081` live, `:30082` preview |
| Canary | Traffic shifted 10% → 50% → 100%, checked at each step, then promoted | Canary weight set to 0 | Host `canary.aceest.local` |
| A/B testing | Header `X-User-Group: B` routes to the new version | Remove the variant ingress | Host `ab.aceest.local` |
| Shadow | Live traffic mirrored to the new version; users only see stable responses | Users are never affected | Host `shadow.aceest.local` |

Example:

```bash
curl http://$(minikube ip):30080/version
curl -H "Host: canary.aceest.local" http://$(minikube ip)/version
curl -H "Host: ab.aceest.local" -H "X-User-Group: B" http://$(minikube ip)/version
```

## Running Locally

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m pytest -v --cov=ACEest_Fitness
python ACEest_Fitness.py            # http://localhost:5000
```

With Docker:

```bash
docker run -p 5000:5000 ajith0b1m/aceest-fitness:2.0.0
```

## Jenkins Prerequisites

- Plugins: Pipeline, Git, JUnit, Docker Pipeline, SonarQube Scanner
- Credentials: `dockerhub` (username + token), `sonar-token` (secret text),
  `kubeconfig` (secret file)
- SonarQube server named `sonarqube`, scanner tool named `sonar-scanner`
- The `jenkins` user must be in the `docker` group
