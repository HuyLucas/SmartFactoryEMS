# Industrial Energy Management System (EMS)

Offline-first LAN dashboard for monitoring energy usage in a mechanical repair factory workshop.

## Project Structure

- `backend/` Django + DRF + Channels backend
- `frontend/` React + Tailwind + Recharts dashboard
- `fake_generator.py` Data simulator that posts telemetry every 5 seconds

## Demo Accounts

- Admin: `admin` / `Admin123!`
- Engineer: `engineer` / `Engineer123!`
- Operator: `operator` / `Operator123!`

## Quick Start (Ubuntu / Windows WSL)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8000
```

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open: `http://SERVER_IP:5173`

## Reports

- Daily CSV: `GET /api/reports/daily/`
- Daily PDF: `GET /api/reports/daily/?format=pdf`
- Monthly CSV: `GET /api/reports/monthly/`
- Monthly PDF: `GET /api/reports/monthly/?format=pdf`

## Fake Generator

```bash
python fake_generator.py
```
