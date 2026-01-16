"""
Flask API Endpoints for Advanced Student Dashboard Features
Add these endpoints to backend/app.py to support the new widgets

Database tables required (run schema_enhancements.sql first):
- company_visits
- notifications
- interview_experiences
- resume_scores
- student_skill_assessments
- Extended applications table with interview fields
"""

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date
from models import *  # Import all SQLAlchemy models

# ============================================================================
# STUDENT DASHBOARD SUMMARY ENDPOINT
# ============================================================================

@app.route('/api/student/dashboard-summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """Get summary stats for student dashboard"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    total_applications = Application.query.filter_by(student_id=student.id).count()
    shortlisted = Application.query.filter(
        Application.student_id == student.id,
        Application.status.in_(['Shortlisted', 'Interview'])
    ).count()
    selected = Application.query.filter(
        Application.student_id == student.id,
        Application.status == 'Selected'
    ).count()
    
    # Get available jobs count
    eligible_jobs = Job.query.filter(
        Job.status == 'Active',
        (Job.min_cgpa is None) | (Job.min_cgpa <= student.cgpa)
    ).count()
    
    return jsonify({
        'eligible_jobs': eligible_jobs,
        'total_applications': total_applications,
        'shortlisted': shortlisted,
        'selected': selected
    })


# ============================================================================
# COMPANY VISITS (DRIVE FEED) ENDPOINTS
# ============================================================================

@app.route('/api/student/company-visits/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_drives():
    """Get upcoming company visits for student's branch"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get future company visits
    future_visits = CompanyVisit.query.filter(
        CompanyVisit.visit_date >= date.today(),
        CompanyVisit.status.in_(['Scheduled', 'Ongoing'])
    ).order_by(CompanyVisit.visit_date).all()
    
    result = []
    for visit in future_visits:
        company = Company.query.get(visit.company_id)

        visit_time_str = None
        if visit.visit_time:
            try:
                visit_time_str = visit.visit_time.strftime('%H:%M')
            except Exception:
                visit_time_str = str(visit.visit_time)

        result.append({
            'id': visit.id,
            'company_name': company.company_name if company else None,
            'company_logo_url': company.logo_url if company else None,
            'recruitment_type': visit.recruitment_type,
            'visit_date': visit.visit_date.isoformat(),
            'visit_time': visit_time_str or 'TBD',
            'location': visit.location or 'TBD',
            'description': visit.description,
            'expected_ctc_range': visit.expected_ctc_range,
            'eligibility_criteria': visit.eligibility_criteria,
            'status': visit.status,
            'created_at': visit.created_at.isoformat() if getattr(visit, 'created_at', None) else None
        })
    
    return jsonify(result)


@app.route('/api/student/company-visits/<int:visit_id>/register', methods=['POST'])
@jwt_required()
def register_drive_interest(visit_id):
    """Register student interest in a company visit"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    visit = CompanyVisit.query.get(visit_id)
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404

    company = Company.query.get(visit.company_id)
    company_name = company.company_name if company else 'Company'
    
    # Create notification for student
    notification = Notification(
        student_id=student.id,
        type='company_visit',
        title=f'Registered for {company_name}',
        message=f'You have registered for the recruitment drive on {visit.visit_date}',
        related_entity_type='company_visit',
        related_entity_id=visit_id,
        priority='medium'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'status': 'registered', 'notification_id': notification.id}), 201


# ============================================================================
# NOTIFICATIONS ENDPOINTS
# ============================================================================

@app.route('/api/student/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get student notifications with filtering"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Query parameters
    unread_only = request.args.get('unread') == 'true'
    notif_type = request.args.get('type')
    
    query = Notification.query.filter_by(student_id=student.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    if notif_type:
        query = query.filter_by(type=notif_type)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    
    result = []
    for notif in notifications:
        result.append({
            'id': notif.id,
            'type': notif.type,
            'title': notif.title,
            'message': notif.message,
            'is_read': notif.is_read,
            'priority': notif.priority,
            'action_url': notif.action_url,
            'created_at': notif.created_at.isoformat(),
            'related_entity_type': notif.related_entity_type,
            'related_entity_id': notif.related_entity_id
        })
    
    return jsonify(result)


@app.route('/api/student/notifications/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notif_id):
    """Mark notification as read"""
    notification = Notification.query.get(notif_id)
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'status': 'marked_read'})


@app.route('/api/student/notifications/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all unread notifications as read"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    Notification.query.filter(
        Notification.student_id == student.id,
        Notification.is_read == False
    ).update({'is_read': True})
    
    db.session.commit()
    
    return jsonify({'status': 'all_marked_read'})


# ============================================================================
# INTERVIEW EXPERIENCE REPOSITORY ENDPOINTS
# ============================================================================

@app.route('/api/interviews', methods=['GET'])
def get_interview_experiences():
    """Get public interview experiences with filtering"""
    # Filter parameters
    company = request.args.get('company')
    difficulty = request.args.get('difficulty')
    interview_type = request.args.get('type')
    search = request.args.get('search')
    
    query = InterviewExperience.query.filter_by(is_public=True)
    
    if company:
        query = query.filter(InterviewExperience.company_name.ilike(f'%{company}%'))
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    if interview_type:
        query = query.filter_by(interview_type=interview_type)
    
    if search:
        query = query.filter(
            (InterviewExperience.topics_covered.ilike(f'%{search}%')) |
            (InterviewExperience.experience_summary.ilike(f'%{search}%'))
        )
    
    experiences = query.order_by(InterviewExperience.created_at.desc()).limit(50).all()
    
    result = []
    for exp in experiences:
        company = Company.query.get(exp.company_id)
        result.append({
            'id': exp.id,
            'company_name': company.company_name if company else 'Unknown',
            'interview_type': exp.interview_type,
            'interview_round': exp.interview_round,
            'difficulty_level': exp.difficulty_level,
            'duration_minutes': exp.duration_minutes,
            'topics_covered': exp.topics_covered,
            'experience_summary': exp.experience_summary,
            'questions_asked': exp.questions_asked,
            'tips_advice': exp.tips_advice,
            'outcome': exp.outcome,
            'rating': exp.rating,
            'interview_date': exp.interview_date.isoformat() if exp.interview_date else None,
            'created_at': exp.created_at.isoformat()
        })
    
    return jsonify(result)


@app.route('/api/student/interview-experience', methods=['POST'])
@jwt_required()
def create_interview_experience():
    """Create new interview experience entry"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    data = request.get_json()
    
    interview = InterviewExperience(
        student_id=student.id,
        company_id=data.get('company_id'),
        job_id=data.get('job_id'),
        interview_round=data.get('interview_round', 1),
        interview_type=data.get('interview_type'),
        difficulty_level=data.get('difficulty_level'),
        duration_minutes=data.get('duration_minutes'),
        topics_covered=data.get('topics_covered'),
        experience_summary=data.get('experience_summary'),
        questions_asked=data.get('questions_asked'),
        tips_advice=data.get('tips_advice'),
        outcome=data.get('outcome'),
        rating=data.get('rating'),
        interview_date=datetime.fromisoformat(data.get('interview_date')) if data.get('interview_date') else None,
        is_public=data.get('is_public', True)
    )
    
    db.session.add(interview)
    db.session.commit()
    
    return jsonify({
        'id': interview.id,
        'status': 'created'
    }), 201


# ============================================================================
# RESUME SCORING ENDPOINTS (MOCK)
# ============================================================================

@app.route('/api/student/resume-score/<int:job_id>', methods=['GET'])
@jwt_required()
def get_resume_score(job_id):
    """Get stored resume score for a job"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    score = ResumeScore.query.filter(
        ResumeScore.student_id == student.id,
        ResumeScore.job_id == job_id
    ).first()
    
    if not score:
        return jsonify({'error': 'Score not found'}), 404
    
    return jsonify({
        'id': score.id,
        'job_id': score.job_id,
        'overall_match_percentage': score.overall_match_percentage,
        'skills_match_percentage': score.skills_match_percentage,
        'experience_match_percentage': score.experience_match_percentage,
        'education_match_percentage': score.education_match_percentage,
        'missing_keywords': score.missing_keywords,
        'matched_keywords': score.matched_keywords,
        'improvement_suggestions': score.improvement_suggestions,
        'assessed_at': score.assessed_at.isoformat()
    })


@app.route('/api/student/resume-score', methods=['POST'])
@jwt_required()
def calculate_resume_score():
    """Calculate resume match score (MOCK - use real AI library in production)"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    data = request.get_json()
    job_description = data.get('job_description', '').lower()
    job_id = data.get('job_id')
    
    # Mock algorithm: keyword matching
    student_skills = student.skills.split(',') if student.skills else []
    
    # Extract keywords from job description
    job_keywords = set(job_description.split())
    skill_keywords = set(' '.join(student_skills).lower().split())
    
    matched = skill_keywords.intersection(job_keywords)
    missing = job_keywords - skill_keywords
    
    match_percentage = int(len(matched) / len(job_keywords) * 100) if job_keywords else 0
    
    # Save score
    score = ResumeScore(
        student_id=student.id,
        job_id=job_id,
        overall_match_percentage=match_percentage,
        skills_match_percentage=match_percentage,
        missing_keywords=list(list(missing)[:10]),  # Top 10 missing
        matched_keywords=list(matched),
        improvement_suggestions=[
            f"Learn: {list(missing)[0]}" if missing else "Great match!",
            "Gain more projects experience"
        ],
        assessed_at=datetime.utcnow()
    )
    
    db.session.add(score)
    db.session.commit()
    
    return jsonify({
        'id': score.id,
        'overall_match_percentage': match_percentage,
        'matched_keywords': list(matched)[:10],
        'missing_keywords': list(missing)[:10],
        'status': 'scored'
    }), 201


# ============================================================================
# SKILL ASSESSMENT ENDPOINTS
# ============================================================================

@app.route('/api/student/skills', methods=['GET'])
@jwt_required()
def get_student_skills():
    """Get student's skill assessments with market demand"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    skills = StudentSkillAssessment.query.filter_by(student_id=student.id).all()
    
    result = []
    for skill in skills:
        result.append({
            'id': skill.id,
            'skill_name': skill.skill_name,
            'proficiency_level': skill.proficiency_level,
            'years_of_experience': skill.years_of_experience,
            'market_demand_level': skill.market_demand_level,
            'endorsements': skill.endorsements,
            'assessment_date': skill.assessment_date.isoformat()
        })
    
    return jsonify(result)


@app.route('/api/student/skills', methods=['POST'])
@jwt_required()
def add_student_skill():
    """Add or update student skill assessment"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    data = request.get_json()
    
    # Check if skill exists
    skill = StudentSkillAssessment.query.filter(
        StudentSkillAssessment.student_id == student.id,
        StudentSkillAssessment.skill_name == data.get('skill_name')
    ).first()
    
    if skill:
        skill.proficiency_level = data.get('proficiency_level', skill.proficiency_level)
        skill.years_of_experience = data.get('years_of_experience', skill.years_of_experience)
    else:
        skill = StudentSkillAssessment(
            student_id=student.id,
            skill_name=data.get('skill_name'),
            proficiency_level=data.get('proficiency_level', 'Beginner'),
            years_of_experience=data.get('years_of_experience', 0),
            market_demand_level=data.get('market_demand_level', 'Medium'),
            endorsements=0,
            assessment_date=datetime.utcnow()
        )
        db.session.add(skill)
    
    db.session.commit()
    
    return jsonify({
        'id': skill.id,
        'skill_name': skill.skill_name,
        'status': 'saved'
    }), 201


# ============================================================================
# APPLICATIONS WITH EXTENDED FIELDS
# ============================================================================

@app.route('/api/student/applications', methods=['GET'])
@jwt_required()
def get_student_applications():
    """Get all student applications with interview details"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    applications = Application.query.filter_by(student_id=student.id).order_by(
        Application.applied_at.desc()
    ).all()
    
    result = []
    for app in applications:
        job = Job.query.get(app.job_id)
        company = Company.query.get(job.company_id) if job else None
        
        result.append({
            'id': app.id,
            'job_id': app.job_id,
            'job_title': job.title if job else 'Unknown',
            'company_name': company.company_name if company else 'Unknown',
            'status': app.status,
            'applied_at': app.applied_at.isoformat(),
            'interview_date': app.interview_date.isoformat() if app.interview_date else None,
            'interview_location': app.interview_location,
            'interview_type': app.interview_type,
            'resume_matched_score': app.resume_matched_score,
            'feedback': app.feedback,
            'notes': app.notes,
            'updated_at': app.updated_at.isoformat()
        })
    
    return jsonify(result)


@app.route('/api/student/applications/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application(app_id):
    """Update application with interview details"""
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    app = Application.query.filter(
        Application.id == app_id,
        Application.student_id == student.id
    ).first()
    
    if not app:
        return jsonify({'error': 'Application not found'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        app.status = data['status']
    if 'interview_date' in data and data['interview_date']:
        app.interview_date = datetime.fromisoformat(data['interview_date'])
    if 'interview_location' in data:
        app.interview_location = data['interview_location']
    if 'interview_type' in data:
        app.interview_type = data['interview_type']
    if 'resume_matched_score' in data:
        app.resume_matched_score = data['resume_matched_score']
    if 'feedback' in data:
        app.feedback = data['feedback']
    
    app.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'status': 'updated'})
