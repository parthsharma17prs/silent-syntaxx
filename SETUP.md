# Placement and Internship Management Portal - Setup Guide

## Quick Start Guide

### Step 1: Database Setup

1. Install MySQL and start the MySQL service
2. Create the database:
```bash
mysql -u root -p
CREATE DATABASE placement_portal;
exit
```

3. Import the schema:
```bash
mysql -u root -p placement_portal < database/schema.sql
```

### Step 2: Backend Setup

1. Navigate to backend folder:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Copy the example file
copy .env.example .env

# Edit .env file with your settings:
# - Change DB_PASSWORD to your MySQL password
# - Update SECRET_KEY and JWT_SECRET_KEY with random strings
```

5. Run the Flask server:
```bash
python app.py
```

Backend will start on http://localhost:5000

### Step 3: Frontend Setup

This repo uses a unified frontend:

1) Frontend (Landing + Portal) (React/Vite):
```bash
PowerShell -ExecutionPolicy Bypass -File .\start_frontend.ps1
```
Frontend will start on http://localhost:3000
Portal will be available at http://localhost:3000/portal/index.html

### Step 4: Access the Application

1. Open the landing page at http://localhost:3000
2. Click **Login/Get Started** to open the portal at http://localhost:3000/portal/index.html
3. Use the demo credentials to login:

**Admin:**
- Email: admin@university.edu
- Password: admin123

**Student:**
- Email: student@university.edu
- Password: student123

**Company:**
- Email: company@tech.com
- Password: company123

## Features Overview

### Student Features
- ✅ View and apply to eligible jobs
- ✅ Track application status (Kanban board)
- ✅ Complete profile with resume upload
- ✅ One-click apply based on eligibility criteria
- ✅ View announcements

### Company Features
- ✅ Post job listings (requires admin approval)
- ✅ View and manage applicants
- ✅ Filter applicants by status
- ✅ Update applicant status through workflow
- ✅ Export applicants data
- ✅ Manage company profile

### Admin Features
- ✅ Verify student and company accounts
- ✅ Approve/reject job postings
- ✅ View placement analytics with charts
- ✅ Branch-wise placement statistics
- ✅ Create announcements for different user groups
- ✅ View overall system statistics

## Technology Stack

### Frontend
- React 18
- React Router v6
- Axios for API calls
- React Hot Toast for notifications
- Recharts for analytics
- React Icons

### Backend
- Flask 3.0
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (Authentication)
- Flask-CORS
- PyMySQL (MySQL connector)

### Database
- MySQL 8.0

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Student Endpoints
- `GET /api/student/profile` - Get student profile
- `PUT /api/student/profile` - Update student profile
- `GET /api/student/jobs` - Get eligible jobs
- `POST /api/student/apply/:jobId` - Apply to job
- `GET /api/student/applications` - Get applications

### Company Endpoints
- `GET /api/company/profile` - Get company profile
- `PUT /api/company/profile` - Update company profile
- `GET /api/company/jobs` - Get company jobs
- `POST /api/company/jobs` - Create job posting
- `GET /api/company/job/:jobId/applicants` - Get applicants
- `PUT /api/company/applicant-status` - Update applicant status

### Admin Endpoints
- `GET /api/admin/pending-users` - Get unverified users
- `PUT /api/admin/verify-user/:userId` - Verify user
- `GET /api/admin/pending-jobs` - Get pending job approvals
- `PUT /api/admin/approve-job/:jobId` - Approve/reject job
- `GET /api/admin/analytics` - Get placement analytics
- `GET /api/admin/announcements` - Get announcements
- `POST /api/admin/announcements` - Create announcement

## Design System

### Colors
- Primary Blue: #1E40AF
- Success Green: #10B981
- Background: #F9FAFB
- Text: #334155

### Typography
- System font stack for clean, professional appearance

### Components
- Consistent 8px border radius
- Subtle drop shadows
- Smooth transitions and hover effects
- Toast notifications for all actions
- Skeleton loaders for async operations

## Troubleshooting

### Database Connection Issues
- Ensure MySQL service is running
- Check DB_PASSWORD in .env file
- Verify database exists: `SHOW DATABASES;`

### Backend Issues
- Activate virtual environment before running
- Check if all dependencies are installed
- Verify port 5000 is not in use

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if backend is running on port 5000
- Clear browser cache

## Future Enhancements

- Email notifications for application status changes
- Resume parsing and automatic skill extraction
- Interview scheduling calendar
- Chat system between students and recruiters
- Advanced filtering and search
- Mobile app support
- Reports generation (PDF/Excel)

## Support

For issues or questions, please refer to the code comments or create an issue in the repository.

---

Built with ❤️ for University Placement Management
