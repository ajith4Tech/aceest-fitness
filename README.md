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
├── k8s/
│   ├── rolling-update/            # Deployment + NodePort service
│   ├── blue-green/                # Blue and green deployments, live + preview services
│   ├── progressive/               # Stable, new and shadow backends
│   ├── canary/                    # Weighted canary ingress
│   ├── ab-testing/                # Header-based A/B ingress
│   ├── shadow/                    # Traffic-mirroring ingress
│   └── scripts/                   # Deploy, verify and rollback script per strategy
└── docs/
    ├── sonarqube/                 # SonarQube analysis results
    └── screenshots/               # Numbered evidence screenshots (see Evidence)
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

SonarQube results (quality gate passed, 94.7% coverage) are in [`docs/sonarqube/`](docs/sonarqube/).

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

## Evidence

**CI/CD**

- [01 Pipeline stages](docs/screenshots/01-jenkins-pipeline-stages-all-green.png) — all stages green, including Deploy to Kubernetes and Smoke Test
- [02 Job overview](docs/screenshots/02-jenkins-job-test-trend-quality-gate.png) — test result trend and SonarQube Quality Gate badge
- [19 Build time trend](docs/screenshots/19-jenkins-build-time-trend.png) — builds #1–#20 across all strategies

**Code quality**

- [SonarQube projects overview](docs/sonarqube/sonarqube-projects-overview.png) — ACEest Fitness, quality gate passed
- [SonarQube quality gate](docs/sonarqube/sonarqube-quality-gate-passed.png) — all conditions passed, 94.7% coverage, 0.0% duplication

**Registry**

- [03 Docker Hub tags](docs/screenshots/03-dockerhub-tags-all-versions.png) — `1.0.0`, `1.1.0`, `1.2.0`, `2.0.0` and `latest`

**Deployment strategies**

- [04 Rolling rollback](docs/screenshots/04-rolling-rollback-1.1.0-to-1.0.0.png) — traffic moves from 1.1.0 back to 1.0.0 with no failed requests
- [05 Rolling update](docs/screenshots/05-rolling-update-1.0.0-to-1.1.0.png) — pods replaced gradually, 1.0.0 → 1.1.0
- [06 Rolling update via Jenkins](docs/screenshots/06-rolling-jenkins-update-to-1.2.0.png) — build #12 rolls out 1.2.0
- [07 Blue-green manual switch](docs/screenshots/07-bluegreen-manual-switch-to-green.png) — preview tested, live switched 1.0.0 → 1.1.0 in one step
- [08 Blue-green via Jenkins](docs/screenshots/08-bluegreen-jenkins-live-on-blue-1.1.0.png) — build #9, live on blue (1.1.0), green kept for rollback
- [09 Blue-green zero-downtime switch](docs/screenshots/09-bluegreen-jenkins-switch-1.1.0-to-1.2.0.png) — live traffic 1.1.0 → 1.2.0 during build #13
- [10 Canary 10% and rollback](docs/screenshots/10-canary-manual-10-percent-and-rollback.png) — ~10% to 1.1.0, then weight 0 returns all traffic to 1.0.0
- [11 Canary 50%](docs/screenshots/11-canary-manual-50-percent.png) — 50/50 split
- [12 Canary 100%](docs/screenshots/12-canary-manual-100-percent.png) — all traffic on 1.1.0
- [13 Canary via Jenkins (1.1.0)](docs/screenshots/13-canary-jenkins-promote-1.1.0.png) — build #10, 10% → 50% → 100%, promoted
- [14 Canary via Jenkins (2.0.0)](docs/screenshots/14-canary-jenkins-promote-2.0.0.png) — build #19, 2.0.0 promoted to stable
- [15 A/B testing](docs/screenshots/15-ab-testing-group-b-1.1.0.png) — group A gets 1.0.0, group B gets 1.1.0 and `/programs`
- [16 Shadow manual demo](docs/screenshots/16-shadow-manual-mirrored-requests.png) — users get 1.0.0, shadow pod log shows mirrored requests
- [17 Shadow via Jenkins (1.1.0)](docs/screenshots/17-shadow-jenkins-1.1.0.png) — build #11, 10 requests mirrored
- [18 Shadow via Jenkins (2.0.0)](docs/screenshots/18-shadow-jenkins-2.0.0.png) — build #18, 10 requests mirrored to 2.0.0

**Public endpoints**

- [20 Public endpoint checks](docs/screenshots/20-public-endpoints-curl-checks.png) — curl from another network against the Cloudflare URLs

## Live Endpoints

Hosted on Minikube behind Cloudflare Tunnel; URLs are refreshed here if a tunnel restarts.

| Strategy | URL | Expected result |
|----------|-----|-----------------|
| Rolling update | https://asus-copied-adjust-subscriptions.trycloudflare.com/version | `2.0.0` |
| Blue-green (live) | https://sets-showcase-accept-night.trycloudflare.com/version | `2.0.0` (green) |
| Blue-green (preview) | https://depends-cycle-mission-believes.trycloudflare.com/version | `1.2.0` (blue, rollback target) |
| Canary | https://bearing-reserved-posing-interior.trycloudflare.com/version | ~80% `1.2.0` / ~20% `2.0.0` |
| A/B testing | https://patent-municipality-vatican-algebra.trycloudflare.com/version | `1.2.0`; with header `X-User-Group: B` → `2.0.0` |
| Shadow | https://clan-document-angel-corporations.trycloudflare.com/version | `1.2.0` to users, mirrored to shadow `2.0.0` |

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
