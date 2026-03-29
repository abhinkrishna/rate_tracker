# Rate Tracker

A robust platform for tracking exchange rates across various providers and rate types. This application features a Django-powered backend with Celery for asynchronous data ingestion and a Next.js frontend.

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** must be installed on your machine.

### How to Run Locally

To spin up the entire stack (PostgreSQL, Redis, Backend, Workers, and Beat):

1.  **Build and Start:**
    ```bash
    docker-compose up --build
    ```
2.  **Debug:**
    If the initial build/startup fails, try:
    ```bash
    docker-compose up
    ```

The backend API will be available at `http://localhost:8000`.

### Seeding Data

Historical data can be seeded from a Parquet file using a management command. This triggers a Celery task chain for non-blocking processing:

```bash
docker compose exec rate_tracker_backend python manage.py seed_data
```

docker command line should start showing the logs of the seed data process.

Login credentials for [admin](http://localhost:8000/admin/)

```
url : http://localhost:8000/admin/
username : root
password : root
```

### Running Tests

To execute the test suite in the backend container:

```bash
docker compose exec rate_tracker_backend python manage.py test
```

## 🏗️ Architectural Choices

### Non-blocking Data Ingestion

The system is designed to handle high-volume data ingestion without blocking the main application.

- **Celery Task Chain:** Data from the seed Parquet file is processed via a 3-step Celery task chain (`Ingest` -> `Validate` -> `Organize`).
- **Rationale:** Offloading heavy I/O and processing jobs to dedicated workers ensures the Django application remains responsive. Using a chain ensures that each step only proceeds upon the successful completion of the previous one, maintaining data integrity.

For a deep dive into the engineering design decisions, please refer to [DECISIONS.md](./DECISIONS.md).

## 📊 Project Scope

### What is Completed:

- Core Backend API (Latest Rates, Historical Trends, Ingestion Webhook).
- Asynchronous Ingestion Pipeline (Parquet support, Validation, Normalization).
- Database Schema with Alias support for messy data sources.
- JWT and Token Authentication.
- Redis-based Caching for Latest Rates.

### What is Pending / Future Scope:

- **API/Socket Ingestion:** Currently, `ingest_api` and `ingest_socket` are dummy implementations. I would have implemented real-time scrapers or API connectors for real-world sources.
- **Enhanced Error Handling:** While basic retries exist in Celery, more robust dead-letter queues and alerting would be added for a production environment.
- **Frontend Integration:** Full integration of the Next.js dashboard with the authenticated API endpoints.

---

_Note: Incomplete scope was a conscious trade-off to focus on the robust architecture and data integrity of the backend pipeline within the allocated time._
