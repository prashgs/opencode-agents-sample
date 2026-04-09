# Build an Expense Tracker

Build a personal expense tracker with a Python FastAPI backend and SQLite database.

## Frontend Features
- Dashboard: total spent this month, top category, transaction count
- Add expense form: amount, category (dropdown), description, date picker
- Expenses table: sortable by date or amount, with delete button per row
- Spending by category: horizontal CSS bar chart (no external chart library)
- Month filter: dropdown to filter by month (current month default)
- Error messages shown inline if API calls fail

## Backend (FastAPI + SQLite)
REST API endpoints:
- GET  /health               — health check
- GET  /expenses             — list all (supports ?month=YYYY-MM query param)
- POST /expenses             — create expense {amount, category, description, date}
- DELETE /expenses/{id}      — delete expense
- GET  /summary              — {total, by_category: {name: amount}, monthly: [{month, total}]}

Store data in data/expenses.db using SQLite.
Enable CORS for all origins.

## Design
Dark theme: #1a1a2e background, #16213e cards, #e94560 accent red.
White text. Monospace font (JetBrains Mono from Google Fonts) for numbers.
Financial dashboard feel.

## Technical
Backend: FastAPI, runs on port 8000 via `bash run.sh`
Frontend: calls http://localhost:8000 API. HTML/CSS/JS — no framework.
Files: index.html, style.css, app.js, app.py, models.py, database.py, requirements.txt, run.sh
