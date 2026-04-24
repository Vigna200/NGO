# NGO Community Response Platform

This application converts scattered NGO field reports into operational decisions:

- ingest text, PDF, and image-based reports
- extract community needs with rule-based AI
- score urgency and impact
- match volunteers based on skills, proximity, and availability
- generate actionable tasks
- manage assignments and task progress in a dashboard

## Why this is more real-world ready

- persistent JSON-backed storage keeps tasks, cases, and volunteers after restart
- manual reassignment allows coordinators to override AI decisions
- task status flow supports action tracking from intake to completion
- dashboard summarizes urgent work, impact, location clusters, and recent cases
- file ingestion supports realistic NGO data collection formats

## Backend

Run from `backend/`:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

API endpoints:

- `POST /upload`
- `GET /tasks`
- `GET /volunteers`
- `POST /assign`
- `POST /tasks/<task_id>/status`
- `GET /dashboard`

## Frontend

Run from `frontend/`:

```powershell
npm install
npm run dev
```

## Suggested next production upgrades

- move persistence from JSON to PostgreSQL
- add authentication and role-based access
- store report attachments in cloud storage
- add geocoding and map visualization
- integrate WhatsApp/SMS/email alerts for urgent cases
- add audit logs and exportable reports
