# Placement and Internship Management Portal

A comprehensive university placement portal with modern UI/UX, built with React, Flask, and MySQL.

## Features

### Student Dashboard
- View and apply to eligible jobs
- Application status tracker (Kanban-style)
- Profile management with resume upload
- One-click apply based on eligibility

### Company Dashboard
- Post and manage job listings
- View and filter applicants
- Applicant workflow management (Applied → Shortlisted → Interview → Selected)
- Export applicant data to Excel

### Admin Dashboard
- Approve job postings
- Verify student and company accounts
- View placement analytics and statistics
- Broadcast announcements

## Tech Stack

- **Frontend (Landing + Portal)**: React + Vite + Tailwind (in `frontend/`)
- **Portal UI pages**: Static HTML/CSS/JS served from `frontend/public/portal/`
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### Database Setup

1. Create MySQL database:
```sql
CREATE DATABASE placement_portal;
```

2. Import the schema:
```bash
mysql -u root -p placement_portal < database/schema.sql
```

### Backend Setup

1. Navigate to backend folder:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run Flask server:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

Unified frontend (landing + portal):
- Run `start_frontend.ps1` → http://localhost:3000/
- Portal is available at http://localhost:3000/portal/index.html

## Default Credentials

### Admin
- Email: admin@university.edu
- Password: admin123

### Test Student
- Email: student@university.edu
- Password: student123

### Test Company
- Email: company@tech.com
- Password: company123

## Design System

- **Primary Color**: Deep Royal Blue (#1E40AF)
- **Success Color**: Emerald Green (#10B981)
- **Background**: White/Light Grey (#F9FAFB)
- **Text**: Slate Grey (#334155)
- **Border Radius**: 8px
- **Shadows**: Mild drop shadows for depth

## API Documentation

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Students
- `GET /api/student/jobs` - Get eligible jobs
- `POST /api/student/apply/:jobId` - Apply to job
- `GET /api/student/applications` - Get application status

### Companies
- `POST /api/company/jobs` - Create job posting
- `GET /api/company/applicants/:jobId` - Get job applicants
- `PUT /api/company/applicant-status` - Update applicant status

### Admin
- `GET /api/admin/pending-jobs` - Get jobs pending approval
- `PUT /api/admin/approve-job/:jobId` - Approve job posting
- `GET /api/admin/analytics` - Get placement statistics

## License

MIT License - University Placement Portal 2026
