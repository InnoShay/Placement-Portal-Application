# Placement Portal Application V2

A comprehensive campus placement management system for institutes, companies, and students.

## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: Vue.js (CDN) + Bootstrap 5
- **Database**: SQLite with SQLAlchemy ORM
- **Caching**: Redis
- **Async Jobs**: Celery + Redis
- **Authentication**: JWT-based

## Roles
- **Admin**: Institute placement cell (pre-created, manages everything)
- **Company**: Registers, posts jobs, manages recruitment
- **Student**: Registers, applies for placement drives

## Setup

### Prerequisites
- Python 3.9+
- Redis Server
- Node.js (optional, for development)

### Installation

```bash
# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Start Redis (separate terminal)
redis-server

# Start Celery worker (separate terminal)
cd backend
celery -A app.celery worker --loglevel=info

# Start Celery beat (separate terminal)
cd backend
celery -A app.celery beat --loglevel=info
```

### Default Admin Credentials
- **Email**: admin@placement.com
- **Password**: admin123

## Project Structure
```
├── backend/
│   ├── app.py              # Flask application factory
│   ├── config.py           # Configuration
│   ├── models.py           # Database models
│   ├── create_admin.py     # Admin user creation
│   ├── tasks.py            # Celery tasks
│   ├── routes/
│   │   ├── auth.py         # Authentication
│   │   ├── admin.py        # Admin endpoints
│   │   ├── company.py      # Company endpoints
│   │   └── student.py      # Student endpoints
│   └── utils/
│       ├── cache.py        # Redis caching
│       ├── decorators.py   # Auth decorators
│       └── email.py        # Notifications
├── frontend/
│   └── src/
│       ├── index.html      # Entry point (Jinja2)
│       └── components/     # Vue.js components
└── README.md
```
