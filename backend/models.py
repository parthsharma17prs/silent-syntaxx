from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.SmallInteger, nullable=False)  # 1=Student, 2=Company, 3=Admin
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role_id': self.role_id,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }


class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    enrollment_number = db.Column(db.String(50), unique=True, nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Numeric(3, 2), nullable=False)
    tenth_percentage = db.Column(db.Numeric(5, 2))
    twelfth_percentage = db.Column(db.Numeric(5, 2))
    graduation_year = db.Column(db.Integer, nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'))
    current_year = db.Column(db.SmallInteger)  # 1-4 year of study
    phone = db.Column(db.String(15))
    resume_url = db.Column(db.String(500))
    ats_score = db.Column(db.Integer)  # ATS score 0-100
    ats_feedback = db.Column(db.Text)  # Detailed ATS feedback from Gemini
    ats_calculated_at = db.Column(db.DateTime)  # When ATS was last calculated
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    projects = db.Column(db.Text)
    certifications = db.Column(db.Text)
    linkedin_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    profile_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='student', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'enrollment_number': self.enrollment_number,
            'branch': self.branch,
            'cgpa': float(self.cgpa) if self.cgpa else None,
            'tenth_percentage': float(self.tenth_percentage) if self.tenth_percentage else None,
            'twelfth_percentage': float(self.twelfth_percentage) if self.twelfth_percentage else None,
            'graduation_year': self.graduation_year,
            'current_year': self.current_year,
            'batch_id': self.batch_id,
            'batch_code': self.batch.batch_code if hasattr(self, 'batch') and self.batch else None,
            'phone': self.phone,
            'resume_url': self.resume_url,
            'ats_score': self.ats_score,
            'ats_feedback': self.ats_feedback,
            'ats_calculated_at': self.ats_calculated_at.isoformat() if self.ats_calculated_at else None,
            'skills': self.skills,
            'experience': self.experience,
            'projects': self.projects,
            'certifications': self.certifications,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'profile_completed': self.profile_completed
        }


class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100))
    hr_name = db.Column(db.String(255), nullable=False)
    hr_phone = db.Column(db.String(15))
    company_website = db.Column(db.String(255))
    logo_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='company', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'hr_name': self.hr_name,
            'hr_phone': self.hr_phone,
            'company_website': self.company_website,
            'logo_url': self.logo_url,
            'description': self.description
        }


class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    job_type = db.Column(db.Enum('Internship', 'Full-Time', 'Part-Time'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(255))
    salary_range = db.Column(db.String(100))
    min_cgpa = db.Column(db.Numeric(3, 2), default=0.00)
    eligible_branches = db.Column(db.Text)  # JSON-like format: ["CSE", "IT", "ECE"]
    min_10th_percentage = db.Column(db.Numeric(5, 2))
    min_12th_percentage = db.Column(db.Numeric(5, 2))
    application_deadline = db.Column(db.Date, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('placement_sessions.id'))
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected', 'Closed'), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='job', cascade='all, delete-orphan')
    hiring_rounds = db.relationship('HiringRound', backref='job', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'company_logo': self.company.logo_url if self.company else None,
            'company_website': self.company.company_website if self.company else None,
            'company_industry': self.company.industry if self.company else None,
            'company_description': self.company.description if self.company else None,
            'title': self.title,
            'job_type': self.job_type,
            'description': self.description,
            'requirements': self.requirements,
            'location': self.location,
            'salary_range': self.salary_range,
            'min_cgpa': float(self.min_cgpa),
            'eligible_branches': self.eligible_branches,
            'min_10th_percentage': float(self.min_10th_percentage) if self.min_10th_percentage else None,
            'min_12th_percentage': float(self.min_12th_percentage) if self.min_12th_percentage else None,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'session_id': self.session_id,
            'session_name': self.session.name if hasattr(self, 'session') and self.session else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('placement_sessions.id'))
    status = db.Column(db.Enum('Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected'), default='Applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'job_id', name='unique_application'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'company_name': self.job.company.company_name if self.job and self.job.company else None,
            'session_id': self.session_id,
            'status': self.status,
            'applied_at': self.applied_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes
        }


class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    target_role = db.Column(db.SmallInteger)  # 1=Student, 2=Company, NULL=All
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'target_role': self.target_role,
            'created_at': self.created_at.isoformat()
        }


class HiringRound(db.Model):
    """Represents each round in the hiring process - Enhanced for production use"""
    __tablename__ = 'hiring_rounds'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    # Round Configuration
    round_number = db.Column(db.Integer, nullable=False)
    round_name = db.Column(db.String(255), nullable=False)  # Enhanced
    round_type = db.Column(db.Enum('Online', 'Offline'), nullable=False, default='Online')  # Enhanced
    round_mode = db.Column(db.Enum('MCQ', 'Coding', 'Interview', 'Group Discussion', 'Assignment', 'Case Study', 'Presentation', 'Other'), nullable=False)  # Enhanced
    
    # Round Details
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer)
    evaluation_criteria = db.Column(db.Text)  # JSON string - Enhanced
    is_elimination_round = db.Column(db.Boolean, default=True)  # Enhanced
    
    # Scheduling & Logistics
    scheduled_date = db.Column(db.Date)  # Enhanced
    scheduled_time = db.Column(db.Time)  # Enhanced
    venue = db.Column(db.String(500))  # Enhanced
    
    # Round Status & Metadata
    status = db.Column(db.Enum('Draft', 'Active', 'Completed', 'Cancelled'), default='Draft')  # Enhanced
    min_passing_score = db.Column(db.Numeric(5, 2))  # Enhanced
    max_score = db.Column(db.Numeric(5, 2), default=100.00)  # Enhanced
    
    # Additional Configuration
    configuration = db.Column(db.Text)  # JSON string for flexible configuration - Enhanced
    
    # Audit Fields
    created_by = db.Column(db.Integer)  # Enhanced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Enhanced
    
    # Relationships
    applications_rounds = db.relationship('ApplicationRound', backref='hiring_round', cascade='all, delete-orphan')
    interview_slots = db.relationship('InterviewSlot', backref='hiring_round', cascade='all, delete-orphan')
    candidate_progress = db.relationship('RoundCandidateProgress', backref='round', cascade='all, delete-orphan')  # Enhanced
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'round_number': self.round_number,
            'round_name': self.round_name or self.round_type,  # Fallback to round_type for backward compatibility
            'round_type': self.round_type if hasattr(self, 'round_type') else 'Online',
            'round_mode': self.round_mode if hasattr(self, 'round_mode') else 'Interview',
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'evaluation_criteria': self.evaluation_criteria,
            'is_elimination_round': self.is_elimination_round if hasattr(self, 'is_elimination_round') else True,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time.isoformat() if hasattr(self, 'scheduled_time') and self.scheduled_time else None,
            'venue': self.venue if hasattr(self, 'venue') else None,
            'status': self.status if hasattr(self, 'status') else 'Draft',
            'min_passing_score': float(self.min_passing_score) if hasattr(self, 'min_passing_score') and self.min_passing_score else None,
            'max_score': float(self.max_score) if hasattr(self, 'max_score') and self.max_score else 100.0,
            'configuration': self.configuration if hasattr(self, 'configuration') else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        }


class ApplicationRound(db.Model):
    """Track student's progress through each hiring round"""
    __tablename__ = 'application_rounds'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    hiring_round_id = db.Column(db.Integer, db.ForeignKey('hiring_rounds.id'), nullable=False)
    status = db.Column(db.Enum('Pending', 'Scheduled', 'Completed', 'Passed', 'Failed'), default='Pending')
    score = db.Column(db.Numeric(5, 2))
    feedback = db.Column(db.Text)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    application = db.relationship('Application', backref='round_progresses')
    
    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'hiring_round_id': self.hiring_round_id,
            'status': self.status,
            'score': float(self.score) if self.score else None,
            'feedback': self.feedback,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class InterviewSlot(db.Model):
    """Interview scheduling system"""
    __tablename__ = 'interview_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    hiring_round_id = db.Column(db.Integer, db.ForeignKey('hiring_rounds.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    slot_date = db.Column(db.Date, nullable=False)
    slot_time = db.Column(db.Time, nullable=False)
    interviewer_name = db.Column(db.String(255))
    interviewer_email = db.Column(db.String(255))
    meeting_link = db.Column(db.String(500))  # For online interviews
    location = db.Column(db.String(255))  # For onsite interviews
    max_capacity = db.Column(db.Integer, default=1)
    current_bookings = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('Available', 'Full', 'Completed', 'Cancelled'), default='Available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('InterviewBooking', backref='slot', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'hiring_round_id': self.hiring_round_id,
            'slot_date': self.slot_date.isoformat(),
            'slot_time': str(self.slot_time),
            'interviewer_name': self.interviewer_name,
            'meeting_link': self.meeting_link,
            'location': self.location,
            'max_capacity': self.max_capacity,
            'current_bookings': self.current_bookings,
            'status': self.status
        }


class InterviewBooking(db.Model):
    """Student booking an interview slot"""
    __tablename__ = 'interview_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    interview_slot_id = db.Column(db.Integer, db.ForeignKey('interview_slots.id'), nullable=False)
    application_round_id = db.Column(db.Integer, db.ForeignKey('application_rounds.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.Enum('Confirmed', 'No-Show', 'Rescheduled', 'Completed'), default='Confirmed')
    booking_notes = db.Column(db.Text)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    application_round = db.relationship('ApplicationRound', backref='interview_bookings')
    student = db.relationship('Student', backref='interview_bookings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_slot_id': self.interview_slot_id,
            'student_id': self.student_id,
            'status': self.status,
            'booked_at': self.booked_at.isoformat()
        }


class OfferLetter(db.Model):
    """Digital offer letter management"""
    __tablename__ = 'offer_letters'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Offer details
    designation = db.Column(db.String(255), nullable=False)
    ctc = db.Column(db.String(100), nullable=False)
    annual_ctc = db.Column(db.Numeric(12, 2))
    job_location = db.Column(db.String(255))
    joining_date = db.Column(db.Date)
    notice_period = db.Column(db.Integer)  # Days
    
    # Letter content
    offer_content = db.Column(db.Text, nullable=False)
    template_used = db.Column(db.String(255))
    
    # Status tracking
    status = db.Column(db.Enum('Generated', 'Sent', 'Accepted', 'Rejected', 'Expired'), default='Generated')
    sent_date = db.Column(db.DateTime)
    acceptance_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    application = db.relationship('Application', backref='offer_letters')
    company = db.relationship('Company', backref='offer_letters')
    student = db.relationship('Student', backref='offer_letters')
    
    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'designation': self.designation,
            'ctc': self.ctc,
            'annual_ctc': float(self.annual_ctc) if self.annual_ctc else None,
            'job_location': self.job_location,
            'joining_date': self.joining_date.isoformat() if self.joining_date else None,
            'status': self.status,
            'sent_date': self.sent_date.isoformat() if self.sent_date else None,
            'acceptance_date': self.acceptance_date.isoformat() if self.acceptance_date else None,
            'created_at': self.created_at.isoformat()
        }


# ==================== ADMIN DASHBOARD MODELS ====================

class StudentVerification(db.Model):
    """Document verification queue for newly registered students"""
    __tablename__ = 'student_verification'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True, nullable=False)
    status = db.Column(db.Enum('Pending', 'Verified', 'Rejected'), default='Pending')
    
    # Document details
    marksheet_10th_url = db.Column(db.String(500))
    marksheet_12th_url = db.Column(db.String(500))
    degree_certificate_url = db.Column(db.String(500))
    verification_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin who verified
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='verification_record')
    admin = db.relationship('User', backref='verified_students')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'email': self.student.user.email if self.student and self.student.user else None,
            'enrollment_number': self.student.enrollment_number if self.student else None,
            'branch': self.student.branch if self.student else None,
            'status': self.status,
            'rejection_reason': self.rejection_reason,
            'submitted_at': self.submitted_at.isoformat(),
            'verification_date': self.verification_date.isoformat() if self.verification_date else None
        }


class StudentBlacklist(db.Model):
    """Student account blacklist for disciplinary action"""
    __tablename__ = 'student_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    reason = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical'), default='Medium')
    
    blacklisted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blacklisted_date = db.Column(db.DateTime, default=datetime.utcnow)
    unblacklist_date = db.Column(db.DateTime)  # For temporary blacklisting
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='blacklist_record')
    admin = db.relationship('User', backref='blacklisted_students')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'is_blacklisted': self.is_blacklisted,
            'reason': self.reason,
            'severity': self.severity,
            'blacklisted_date': self.blacklisted_date.isoformat(),
            'unblacklist_date': self.unblacklist_date.isoformat() if self.unblacklist_date else None
        }


class Department(db.Model):
    """Master list of departments/branches"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    total_students = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'total_students': self.total_students,
            'is_active': self.is_active
        }


class BatchYear(db.Model):
    """Master list of batch/graduation years"""
    __tablename__ = 'batch_years'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
    academic_session = db.Column(db.String(20), nullable=False)  # e.g., "2023-2024"
    total_students = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'academic_session': self.academic_session,
            'total_students': self.total_students,
            'is_active': self.is_active
        }


class Skill(db.Model):
    """Master list of technical skills"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., "Programming", "Framework", "Database"
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'is_active': self.is_active
        }


class PlacementStats(db.Model):
    """Aggregated placement statistics for analytics dashboard"""
    __tablename__ = 'placement_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    
    # Overall stats
    total_students = db.Column(db.Integer, default=0)
    placed_students = db.Column(db.Integer, default=0)
    unplaced_students = db.Column(db.Integer, default=0)
    highest_package = db.Column(db.Numeric(12, 2), default=0)
    average_package = db.Column(db.Numeric(12, 2), default=0)
    
    # Department-wise
    department_stats = db.Column(db.JSON)  # {"CSE": {"placed": 50, "total": 80}, ...}
    
    # Company visits
    total_companies_visiting = db.Column(db.Integer, default=0)
    companies_in_interview = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_students': self.total_students,
            'placed_students': self.placed_students,
            'unplaced_students': self.unplaced_students,
            'highest_package': float(self.highest_package) if self.highest_package else 0,
            'average_package': float(self.average_package) if self.average_package else 0,
            'department_stats': self.department_stats,
            'total_companies_visiting': self.total_companies_visiting,
            'companies_in_interview': self.companies_in_interview
        }


class CompanyVisit(db.Model):
    """Track company visits and their current status"""
    __tablename__ = 'company_visits'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    visit_time = db.Column(db.Time)
    location = db.Column(db.String(255))
    description = db.Column(db.Text)

    recruitment_type = db.Column(db.Enum('Walk-in', 'Campus Drive', 'Online'), default='Campus Drive')
    expected_ctc_range = db.Column(db.String(100))
    eligibility_criteria = db.Column(db.Text)

    status = db.Column(db.Enum('Scheduled', 'Ongoing', 'Completed', 'Cancelled'), default='Scheduled')

    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    company = db.relationship('Company', backref='visits')
    
    def to_dict(self):
        visit_time_str = None
        if self.visit_time:
            try:
                visit_time_str = self.visit_time.strftime('%H:%M')
            except Exception:
                visit_time_str = str(self.visit_time)

        return {
            'id': self.id,
            'company_name': self.company.company_name if self.company else None,
            'company_logo': self.company.logo_url if self.company else None,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'visit_time': visit_time_str,
            'status': self.status,
            'location': self.location,
            'description': self.description,
            'recruitment_type': self.recruitment_type,
            'expected_ctc_range': self.expected_ctc_range,
            'eligibility_criteria': self.eligibility_criteria,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class RoundCandidateProgress(db.Model):
    """Model for tracking candidate progress through recruitment rounds"""
    __tablename__ = 'round_candidate_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('hiring_rounds.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Progress Tracking
    status = db.Column(db.Enum('Pending', 'Invited', 'In Progress', 'Completed', 'Passed', 'Failed', 'Absent', 'Disqualified'), default='Pending')
    score = db.Column(db.Numeric(5, 2))
    candidate_rank = db.Column(db.Integer)
    
    # Detailed Evaluation
    evaluator_notes = db.Column(db.Text)
    evaluation_metrics = db.Column(db.Text)  # JSON string
    strengths = db.Column(db.Text)
    areas_of_improvement = db.Column(db.Text)
    
    # Timestamps
    invited_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    evaluated_at = db.Column(db.DateTime)
    
    # Additional Data
    attempt_count = db.Column(db.Integer, default=0)
    submission_data = db.Column(db.Text)  # JSON string
    
    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'round_id': self.round_id,
            'application_id': self.application_id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if hasattr(self, 'student') and self.student else None,
            'status': self.status,
            'score': float(self.score) if self.score else None,
            'candidate_rank': self.candidate_rank,
            'evaluator_notes': self.evaluator_notes,
            'evaluation_metrics': self.evaluation_metrics,
            'strengths': self.strengths,
            'areas_of_improvement': self.areas_of_improvement,
            'invited_at': self.invited_at.isoformat() if self.invited_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
            'attempt_count': self.attempt_count,
            'submission_data': self.submission_data
        }

# Add relationship to Student model for RoundCandidateProgress
Student.round_progress = db.relationship('RoundCandidateProgress', backref='student', cascade='all, delete-orphan')


# =====================================================
# BATCH AND PLACEMENT SESSION MODELS
# =====================================================

class PlacementSession(db.Model):
    """Represents a placement recruitment season (e.g., 2024-25 Placement Season)"""
    __tablename__ = 'placement_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Active', 'Upcoming', 'Archived'), default='Active')
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='session', lazy='dynamic')
    applications = db.relationship('Application', backref='session', lazy='dynamic')
    batch_mappings = db.relationship('BatchSessionMapping', backref='session', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Batch(db.Model):
    """Represents an academic batch (e.g., 2021-2025)"""
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_code = db.Column(db.String(50), unique=True, nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    program = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.Enum('Active', 'Graduated', 'Archived'), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='batch', lazy='dynamic')
    session_mappings = db.relationship('BatchSessionMapping', backref='batch', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_code': self.batch_code,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'degree': self.degree,
            'program': self.program,
            'description': self.description,
            'status': self.status,
            'student_count': self.students.count() if hasattr(self, 'students') else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class BatchSessionMapping(db.Model):
    """Many-to-many relationship between Batches and Placement Sessions"""
    __tablename__ = 'batch_session_mapping'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('placement_sessions.id'), nullable=False)
    is_eligible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('batch_id', 'session_id', name='unique_batch_session'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'session_id': self.session_id,
            'is_eligible': self.is_eligible,
            'created_at': self.created_at.isoformat()
        }


# Update existing models to add batch/session relationships
# These will reference the new foreign keys added via migration

# Note: The following columns will be added via migration:
# - students.batch_id -> FK to batches.id
# - jobs.session_id -> FK to placement_sessions.id  
# - applications.session_id -> FK to placement_sessions.id
