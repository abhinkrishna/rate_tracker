# Rate Tracker

To run the app using docker-compose

```
docker-compose up --build
```

## Backend - Django App

- Project name : rate_tracker
- Django Apps (1) : [ rates ]
- Database : PostgreSQL
- Other major packages : DRF, Celery, Redis
- Celery Workers :
  - IngestService [Ingestion, Validation, Organizer, Cleanup]

## Frontend - Nextjs App

- Project name : rate_tracker_frontend
- Other major packages : HeroUI, TailwindCSS
