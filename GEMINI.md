**update GEMINI.md file if any structure changed**

### Project Structure
```
uscis-tracker/
├── app/
│   ├── __init__.py # App factory
│   ├── config.py # Loads from .env
│   ├── models/
│   │   └── case.py # Reusable Case model
│   ├── blueprints/
│   │   ├── cases/ # CRUD for cases
│   │   ├── api/ # JSON API for Chart.js
│   │   └── dashboard/ # Dashboard + charts
│   ├── services/
│   │   ├── uscis_client.py # USCIS case status checker
│   │   └── chart_service.py # Data aggregation for Chart.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/ # Reusable components
│   │   │   ├── case_card.html
│   │   │   ├── case_form.html
│   │   │   ├── status_badge.html
│   │   │   └── chart_card.html
│   │   ├── cases/
│   │   │   ├── list.html # List and track cases
│   │   │   └── edit.html # Edit case details
│   │   └── dashboard/index.html
│   └── static/
│       ├── js/charts.js # Reusable Chart.js wrapper
│       └── css/styles.css # Premium custom stylesheet
├── migrations/ # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .env # gitignored
└── GEMINI.md # <- The main instruction file
```

### 1. The `GEMINI.md` file

Copy this to your project root as `GEMINI.md`:

```markdown
# GEMINI.md - USCIS Case Tracker (Flask)

## Project Goal
Build a simple Flask app to track USCIS cases: I-485, I-129, I-539, I-765, I-131, etc. Track receipt number, form type, status, history.

## Tech Stack
- Backend: Flask, Flask-SQLAlchemy, Flask-Migrate, python-dotenv
- DB: SQLite for dev, Postgres for Docker prod
- Frontend: Jinja2 + Bootstrap 5 + Chart.js via CDN
- Scheduler: APScheduler to auto-check USCIS status
- Container: Docker + docker-compose

## Security Rules
1. **NEVER hardcode secrets.** All sensitive info must be in `.env`
2. Required.env vars: `SECRET_KEY`, `DATABASE_URL`, `USCIS_API_URL`, `FLASK_ENV`
3. Load via `app/config.py` using `os.getenv`
4. `.env` is in `.gitignore`

## Architecture - Reusability First

### 1. App Factory Pattern
`app/__init__.py` must create app with `create_app()`.

### 2. Config
`app/config.py`:
```python
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cases.db")
    USCIS_API_URL = os.getenv("USCIS_API_URL", "https://egov.uscis.gov/casestatus/mycasestatus.do")
```

### 3. Reusable Model: `app/models/case.py`
Fields: id, receipt_number (unique, indexed), form_type (Enum: I-485, I-129, I-539, I-765, I-131), nickname, current_status, last_checked, created_at, history (JSON field for status timeline)
Methods: `update_status(new_status)` -> appends to history

### 4. Reusable Components (DRY)
- `templates/components/status_badge.html`: macro `render_badge(status)` with color mapping
- `templates/components/case_card.html`: macro `render_case_card(case)`
- `templates/components/case_form.html`: macro `render_case_form(form)`
- `templates/components/chart_card.html`: macro `render_chart_card(chart_id, title)`
- `static/js/charts.js`: reusable functions:
  `createStatusDoughnutChart(ctx, data)`, `createTimelineLineChart(ctx, data)`, `createFormTypeBarChart(ctx, data)`

### 5. Blueprints
- `cases`: `/cases` list, add, edit, delete
- `dashboard`: `/` dashboard with charts
- `api`: `/api/stats`, `/api/cases` returns JSON for Chart.js

### 6. Services
- `uscis_client.py`: `def fetch_case_status(receipt_number):` - handle scraping / API, return status. Mock it if USCIS blocks.
- `chart_service.py`: `get_status_distribution()`, `get_timeline_data()`, `get_form_type_counts()` - returns dict ready for Chart.js

### 7. Chart.js Requirement
Use Chart.js 4.x via CDN in base.html. All charts must get data from `/api/*` via fetch, not inline python. Example in `dashboard/index.html`:
```html
<canvas id="statusChart"></canvas>
<script> fetch('/api/stats').then(r=>r.json()).then(d => createStatusDoughnutChart(...)) </script>
```

### 8. Docker Requirement
- Dockerfile: python:3.11-slim, copy requirements, run gunicorn
- docker-compose.yml: web + db (postgres), volumes, env_file:.env
- Entrypoint runs `flask db upgrade`

## Implementation Steps for Gemini
1. Create.env.example and config
2. Implement model + reusable template macros
3. Implement services
4. Implement blueprints
5. Implement dashboard with 3 charts: Status Doughnut, Cases by Form Type (Bar), Status Timeline (Line)
6. Add Dockerfile and docker-compose.yml
7. Test with `docker-compose up --build`
```

### 2. `.env.example`
```
SECRET_KEY=change-this-to-a-random-string
DATABASE_URL=sqlite:///cases.db
# For docker: DATABASE_URL=postgresql://postgres:postgres@db:5432/cases_db
USCIS_API_URL=https://egov.uscis.gov/casestatus/mycasestatus.do
FLASK_ENV=development
```

### 3. Key Reusable Code Snippets

**`requirements.txt`**
```
Flask
Flask-SQLAlchemy
Flask-Migrate
python-dotenv
requests
beautifulsoup4
APScheduler
gunicorn
psycopg2-binary
```

**`app/models/case.py` - Reusable**
```python
from app import db
from datetime import datetime
class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20), unique=True, nullable=False)
    form_type = db.Column(db.String(20), nullable=False) # I-485, I-129 etc
    nickname = db.Column(db.String(100))
    current_status = db.Column(db.String(200), default="Pending")
    history = db.Column(db.JSON, default=list)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def update_status(self, new_status):
        if not self.history: self.history = []
        self.history.append({"status": new_status, "at": datetime.utcnow().isoformat()})
        self.current_status = new_status
        self.last_checked = datetime.utcnow()
```

**`app/static/js/charts.js` - Reusable Chart.js wrapper**
```javascript
function createStatusDoughnutChart(ctx, data){
  return new Chart(ctx, {
    type: 'doughnut',
    data: { labels: Object.keys(data), datasets: [{ data: Object.values(data) }] }
  });
}
function createFormTypeBarChart(ctx, data){
  return new Chart(ctx, {
    type: 'bar',
    data: { labels: Object.keys(data), datasets: [{ label: 'Cases', data: Object.values(data) }] }
  });
}
```

**`Dockerfile`**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt
COPY..
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

**`docker-compose.yml`**
```yaml
version: '3.8'
services:
  web:
    build:.
    ports: ["5000:5000"]
    env_file:.env
    depends_on: [db]
    volumes: [".:/app"]
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: cases_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes: [pgdata:/var/lib/postgresql/data]
volumes:
  pgdata:
```

### 4. How to run

```bash
cp.env.example.env
# edit SECRET_KEY
pip install -r requirements.txt
flask db init && flask db migrate -m "init" && flask db upgrade
flask run

# Or with Docker:
docker-compose up --build
```

