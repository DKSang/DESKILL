---
name: de-env
description: "Create a reproducible local development environment and produce `docker-compose.yml`, `.env.template`, and `requirements.txt`. Use this skill when the user asks 'how do I set up my environment', 'write a docker-compose for [tools]', 'configure my dev environment', 'what do I need to install', 'how do I containerize my pipeline', or has committed to a tool stack and needs it running locally."
---

# Skill: Setup Development Environment

## Purpose

Create a **reproducible** local environment — anyone who clones the repo can run `docker compose up` and get the same environment, no manual steps. "It works on my machine" is not an acceptable answer.

## When to stop at this skill

Done when `docker compose up` succeeds from a **fresh clone** (not from a machine with pre-installed tools) and the orchestrator UI is accessible.

## Steps

### Step 1 — Identify services that need containerization

From `docs/architecture.md` (tool choices), list the services:

| Tool | Service name | Default port |
|------|-------------|--------------|
| Airflow | airflow-scheduler, airflow-webserver, airflow-worker | 8080 |
| Dagster | dagster-webserver, dagster-daemon | 3000 |
| Prefect | prefect-server | 4200 |
| MinIO | minio | 9000, 9001 |
| PostgreSQL | postgres | 5432 |
| Redis | redis | 6379 |
| Spark | spark-master, spark-worker | 7077, 8081 |
| DuckDB | No container needed — file-based | - |

### Step 2 — Create docker-compose.yml

Rules when writing:
- **Each service gets its own block** with a tool name comment
- **Volumes** for data persistence (data shouldn't disappear on container restart)
- **Health checks** so downstream services know when upstream is ready
- **Env vars** from `.env` file — never hardcode credentials
- **Networks** explicit so services can communicate

### Step 3 — Create .env.template

List **every** environment variable needed:

```bash
# .env.template — copy to .env and fill in values
# NEVER commit .env to git

# Orchestrator
AIRFLOW__CORE__FERNET_KEY=           # Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Source API credentials
SOURCE_API_KEY=                       # From [source name] dashboard
SOURCE_API_SECRET=

# Storage
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
```

### Step 4 — Pin dependencies

Create `requirements.txt` with **pinned versions**:

```
apache-airflow==2.9.0
dbt-core==1.8.0
dbt-duckdb==1.8.0
duckdb==0.10.0
pandas==2.2.0
requests==2.31.0
```

Reason for pinning: `pip install apache-airflow` today may install a different version than 3 months from now → environment is not reproducible.

### Step 5 — Verify from fresh clone

Test acceptance criteria:

```bash
git clone <repo>
cd <project>
cp .env.template .env
# Fill in .env
docker compose up -d
# Wait 30-60s for services to start
curl http://localhost:8080/health  # Or appropriate URL for your tool
```

If any step needs a manual step not in the README → not done yet.

## Output

Create 3 files:

### `docker-compose.yml`

```yaml
# docker-compose.yml — Run: docker compose up -d
# Requires: .env file from .env.template

version: '3.8'

x-common-env: &common-env
  env_file: .env

networks:
  pipeline-net:
    driver: bridge

volumes:
  postgres-data:
  minio-data:
  airflow-logs:

services:

  # ─── PostgreSQL (metadata DB for Airflow) ───
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-airflow}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-airflow}
      POSTGRES_DB: ${POSTGRES_DB:-airflow}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - pipeline-net
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-airflow}"]
      interval: 10s
      retries: 5
      start_period: 5s

  # ─── MinIO (object storage, S3-compatible) ───
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin}
    volumes:
      - minio-data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    networks:
      - pipeline-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      retries: 5

  # ─── Airflow (replace with your chosen orchestrator) ───
  airflow-init:
    image: apache/airflow:2.9.0
    entrypoint: /bin/bash
    command: -c "airflow db init && airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com"
    environment:
      <<: *common-env
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER:-airflow}:${POSTGRES_PASSWORD:-airflow}@postgres/${POSTGRES_DB:-airflow}
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - pipeline-net

  airflow-webserver:
    image: apache/airflow:2.9.0
    command: webserver
    environment:
      <<: *common-env
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER:-airflow}:${POSTGRES_PASSWORD:-airflow}@postgres/${POSTGRES_DB:-airflow}
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - airflow-logs:/opt/airflow/logs
    networks:
      - pipeline-net
    depends_on:
      - airflow-init
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      retries: 5
      start_period: 30s

  airflow-scheduler:
    image: apache/airflow:2.9.0
    command: scheduler
    environment:
      <<: *common-env
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER:-airflow}:${POSTGRES_PASSWORD:-airflow}@postgres/${POSTGRES_DB:-airflow}
    volumes:
      - ./dags:/opt/airflow/dags
      - airflow-logs:/opt/airflow/logs
    networks:
      - pipeline-net
    depends_on:
      - airflow-init
```

## DONE WHEN

- [ ] `docker compose up` succeeds from a fresh clone (nothing pre-installed)
- [ ] `.env.template` has all required environment variables, no hardcoded values
- [ ] `.env` is in `.gitignore`
- [ ] `requirements.txt` pins specific versions
- [ ] Orchestrator UI accessible at `localhost:<port>`

## Next Step

Previous: `/schema`. After done → run `/ingest` to implement the Bronze ingestion layer.

## References

- Template: `skills/env/assets/docker-compose-base.yml` — ready-to-customize template
- Phase deep-dive: `phases/phase-3-environment-setup.md`
- Previous skill: `skills/schema/SKILL.md`
- Next skill: `skills/ingest/SKILL.md`
