"""
Advanced Company Dashboard Routes
Includes: Create Drive Wizard, Advanced Applicant Management, Interview Scheduling, Offer Letters
"""

from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Company, Job, Student, Application, HiringRound, ApplicationRound, InterviewSlot, InterviewBooking, OfferLetter
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import json
import re
from io import BytesIO
import csv

company_bp = Blueprint('company_advanced', __name__, url_prefix='/api/company')

def get_user_id():
    """Get user ID from JWT identity"""
    identity = get_jwt_identity()
    return int(identity) if isinstance(identity, str) else identity


def extract_round_number(status):
    """Extract round number from status string like 'Round 1: Technical' -> 1"""
    if not status:
        return None
    match = re.search(r'Round (\d+):', status)
    if match:
        return int(match.group(1))
    return None

# ==================== CREATE DRIVE WIZARD ====================

@company_bp.route('/create-drive/step1', methods=['POST'])
@jwt_required()
def create_drive_step1():
    """Step 1: Basic Job Details"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        if not company:
            return jsonify({'error': 'Company profile not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required = ['title', 'job_type', 'description', 'ctc', 'location', 'application_deadline']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create job posting
        job = Job(
            company_id=company.id,
            title=data['title'],
            job_type=data['job_type'],
            description=data['description'],
            location=data['location'],
            salary_range=data.get('ctc', ''),
            application_deadline=datetime.strptime(data['application_deadline'], '%Y-%m-%d').date(),
            requirements=data.get('requirements', ''),
            status='Draft'  # Not yet published
        )
        db.session.add(job)
        db.session.flush()
        
        return jsonify({
            'message': 'Job details saved',
            'job_id': job.id,
            'step': 1
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/create-drive/<int:job_id>/step2', methods=['POST'])
@jwt_required()
def create_drive_step2(job_id):
    """Step 2: Eligibility Criteria"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        job = Job.query.filter_by(id=job_id, company_id=company.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        
        # Update eligibility criteria
        job.min_cgpa = data.get('min_cgpa', 0.0)
        job.eligible_branches = json.dumps(data.get('eligible_branches', []))
        job.min_10th_percentage = data.get('min_10th_percentage')
        job.min_12th_percentage = data.get('min_12th_percentage')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Eligibility criteria saved',
            'job_id': job.id,
            'step': 2
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/create-drive/<int:job_id>/step3', methods=['POST'])
@jwt_required()
def create_drive_step3(job_id):
    """Step 3: Hiring Process Configuration"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        job = Job.query.filter_by(id=job_id, company_id=company.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        rounds = data.get('rounds', [])
        
        # Delete existing rounds if any
        HiringRound.query.filter_by(job_id=job_id).delete()
        
        # Create new rounds
        for idx, round_data in enumerate(rounds, 1):
            round_obj = HiringRound(
                job_id=job_id,
                round_number=idx,
                round_type=round_data.get('type', ''),
                description=round_data.get('description', ''),
                duration_minutes=round_data.get('duration_minutes', 60)
            )
            db.session.add(round_obj)
        
        # Publish the job
        job.status = 'Approved'
        db.session.commit()
        
        return jsonify({
            'message': 'Hiring process configured and job published',
            'job_id': job.id,
            'step': 3,
            'total_rounds': len(rounds)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ADVANCED APPLICANT MANAGEMENT ====================

@company_bp.route('/job/<int:job_id>/applicants/advanced', methods=['GET'])
@jwt_required()
def get_applicants_advanced(job_id):
    """Get applicants with advanced filtering and eligibility checking"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        job = Job.query.filter_by(id=job_id, company_id=company.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get query parameters
        hide_ineligible = request.args.get('hide_ineligible', 'false').lower() == 'true'
        sort_by = request.args.get('sort_by', 'applied_at')
        sort_order = request.args.get('sort_order', 'desc')
        filter_cgpa = request.args.get('min_cgpa')
        filter_branch = request.args.get('branch')
        filter_status = request.args.get('status')
        
        # Base query
        query = db.session.query(
            Application.id,
            Application.status,
            Application.applied_at,
            Student.id.label('student_id'),
            Student.full_name,
            Student.enrollment_number,
            Student.branch,
            Student.cgpa,
            Student.phone,
            Student.skills,
            Student.ats_score,
            Student.ats_feedback,
            Student.ats_calculated_at
        ).join(Student, Application.student_id == Student.id).filter(
            Application.job_id == job_id
        )
        
        # Apply filters
        if hide_ineligible:
            job_branches = json.loads(job.eligible_branches) if job.eligible_branches else []
            # Check if branches is set to "All"
            branches_is_all = False
            if job_branches:
                if 'All' in job_branches or 'all' in [str(b).lower() for b in job_branches]:
                    branches_is_all = True
            # Only apply branch filter if not "All"
            if job_branches and not branches_is_all:
                query = query.filter(Student.branch.in_(job_branches))
            if job.min_cgpa:
                query = query.filter(Student.cgpa >= float(job.min_cgpa))
        
        if filter_cgpa:
            query = query.filter(Student.cgpa >= float(filter_cgpa))
        
        if filter_branch:
            query = query.filter(Student.branch == filter_branch)
        
        if filter_status:
            query = query.filter(Application.status == filter_status)
        
        # Apply sorting
        if sort_by == 'cgpa':
            query = query.order_by(Student.cgpa.desc() if sort_order == 'desc' else Student.cgpa.asc())
        elif sort_by == 'name':
            query = query.order_by(Student.full_name.asc() if sort_order == 'asc' else Student.full_name.desc())
        elif sort_by == 'ats_score':
            query = query.order_by(Student.ats_score.desc() if sort_order == 'desc' else Student.ats_score.asc())
        else:
            query = query.order_by(Application.applied_at.desc() if sort_order == 'desc' else Application.applied_at.asc())
        
        applicants = query.all()
        
        # Format response
        result = []
        for app in applicants:
            eligibility = check_eligibility(app, job)
            result.append({
                'application_id': app.id,
                'student_id': app.student_id,
                'name': app.full_name,
                'enrollment': app.enrollment_number,
                'branch': app.branch,
                'cgpa': float(app.cgpa),
                'phone': app.phone,
                'skills': app.skills,
                'status': app.status,
                'applied_at': app.applied_at.isoformat(),
                'eligible': eligibility['is_eligible'],
                'ineligibility_reasons': eligibility['reasons'],
                'ats_score': float(app.ats_score) if app.ats_score is not None else None,
                'ats_feedback': app.ats_feedback,
                'ats_calculated_at': app.ats_calculated_at.isoformat() if app.ats_calculated_at else None,
                'current_round_number': extract_round_number(app.status)
            })
        
        return jsonify({
            'total': len(result),
            'applicants': result,
            'filters_applied': {
                'hide_ineligible': hide_ineligible,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def check_eligibility(applicant, job):
    """Check if an applicant meets job eligibility criteria"""
    reasons = []
    
    try:
        job_branches = json.loads(job.eligible_branches) if job.eligible_branches else []
    except:
        job_branches = []
    
    # Check if branches is set to "All" (skip branch check if so)
    branches_is_all = False
    if job.eligible_branches:
        try:
            # Check if it's a JSON array containing "All"
            if 'All' in job_branches or 'all' in [str(b).lower() for b in job_branches]:
                branches_is_all = True
        except:
            # Check if it's a plain string "All"
            if job.eligible_branches.strip().lower() == 'all':
                branches_is_all = True
    
    if job_branches and applicant.branch not in job_branches and not branches_is_all:
        reasons.append(f'Branch {applicant.branch} not in eligible branches: {", ".join(job_branches)}')
    
    if job.min_cgpa and float(applicant.cgpa) < float(job.min_cgpa):
        reasons.append(f'CGPA {applicant.cgpa} below minimum {job.min_cgpa}')
    
    return {
        'is_eligible': len(reasons) == 0,
        'reasons': reasons
    }


@company_bp.route('/job/<int:job_id>/applicants/download-resumes', methods=['POST'])
@jwt_required()
def download_resumes_zip(job_id):
    """Download all applicant resumes as a ZIP file"""
    try:
        import zipfile
        from io import BytesIO
        
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        job = Job.query.filter_by(id=job_id, company_id=company.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        # Create in-memory ZIP file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            students = Student.query.filter(Student.id.in_(student_ids)).all()
            
            for student in students:
                # Add mock resume data
                resume_content = f"""
RESUME - {student.full_name}

Contact Information:
Email: {student.user.email if student.user else 'N/A'}
Phone: {student.phone}
Branch: {student.branch}

CGPA: {student.cgpa}
Graduation Year: {student.graduation_year}

Skills: {student.skills}
""".encode('utf-8')
                
                zip_file.writestr(f'{student.full_name}_{student.enrollment_number}_resume.txt', resume_content)
        
        zip_buffer.seek(0)
        
        return {
            'message': f'ZIP created with {len(students)} resumes',
            'count': len(students)
        }, 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/job/<int:job_id>/bulk-status-upload', methods=['POST'])
@jwt_required()
def bulk_status_upload(job_id):
    """Upload CSV/Excel file to update application statuses in bulk"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        job = Job.query.filter_by(id=job_id, company_id=company.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Parse CSV data
        stream = file.stream.read().decode('utf8'), 
        csv_data = csv.DictReader(stream)
        
        updates = []
        errors = []
        
        for idx, row in enumerate(csv_data, 1):
            try:
                student_id = int(row.get('student_id', ''))
                new_status = row.get('status', '')
                
                if not new_status in ['Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected']:
                    errors.append(f'Row {idx}: Invalid status "{new_status}"')
                    continue
                
                app = Application.query.filter_by(
                    job_id=job_id,
                    student_id=student_id
                ).first()
                
                if app:
                    app.status = new_status
                    app.updated_at = datetime.utcnow()
                    updates.append(student_id)
                else:
                    errors.append(f'Row {idx}: Student {student_id} application not found')
                    
            except Exception as e:
                errors.append(f'Row {idx}: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Bulk status update completed',
            'updated_count': len(updates),
            'error_count': len(errors),
            'errors': errors[:10]  # Return first 10 errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== INTERVIEW SCHEDULING ====================

@company_bp.route('/job/<int:job_id>/interview-slots', methods=['GET', 'POST'])
@jwt_required()
def manage_interview_slots(job_id):
    """Get or create interview slots"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        job = Job.query.filter_by(id=job_id, company_id=company.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if request.method == 'GET':
            hiring_round_id = request.args.get('hiring_round_id')
            slots = InterviewSlot.query.filter(
                InterviewSlot.company_id == company.id,
                InterviewSlot.hiring_round.has(HiringRound.job_id == job_id)
            )
            
            if hiring_round_id:
                slots = slots.filter_by(hiring_round_id=int(hiring_round_id))
            
            return jsonify([slot.to_dict() for slot in slots.all()]), 200
        
        else:  # POST - Create new slots
            data = request.get_json()
            
            hiring_round = HiringRound.query.get(data.get('hiring_round_id'))
            if not hiring_round or hiring_round.job_id != job_id:
                return jsonify({'error': 'Invalid hiring round'}), 404
            
            slots_to_create = data.get('slots', [])
            created_slots = []
            
            for slot_data in slots_to_create:
                slot = InterviewSlot(
                    hiring_round_id=hiring_round.id,
                    company_id=company.id,
                    slot_date=datetime.strptime(slot_data['date'], '%Y-%m-%d').date(),
                    slot_time=datetime.strptime(slot_data['time'], '%H:%M').time(),
                    interviewer_name=slot_data.get('interviewer_name'),
                    interviewer_email=slot_data.get('interviewer_email'),
                    meeting_link=slot_data.get('meeting_link'),
                    location=slot_data.get('location'),
                    max_capacity=slot_data.get('max_capacity', 1),
                    status='Available'
                )
                db.session.add(slot)
                created_slots.append(slot.to_dict())
            
            db.session.commit()
            
            return jsonify({
                'message': f'{len(created_slots)} interview slots created',
                'slots': created_slots
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/interview-slot/<int:slot_id>/bookings', methods=['GET'])
@jwt_required()
def get_slot_bookings(slot_id):
    """Get all bookings for an interview slot"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        slot = InterviewSlot.query.get(slot_id)
        if not slot or slot.company_id != user.company.id:
            return jsonify({'error': 'Slot not found'}), 404
        
        bookings = InterviewBooking.query.filter_by(interview_slot_id=slot_id).all()
        
        return jsonify({
            'slot': slot.to_dict(),
            'bookings': [b.to_dict() for b in bookings],
            'available_spots': slot.max_capacity - slot.current_bookings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== OFFER LETTER GENERATION ====================

@company_bp.route('/application/<int:application_id>/generate-offer', methods=['POST'])
@jwt_required()
def generate_offer_letter(application_id):
    """Generate an offer letter for a selected candidate"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        app = Application.query.get(application_id)
        if not app or app.job.company_id != company.id:
            return jsonify({'error': 'Application not found'}), 404
        
        data = request.get_json()
        
        # Generate offer letter content
        offer_content = generate_offer_letter_html(
            app.student.full_name,
            data['designation'],
            data['ctc'],
            data['job_location'],
            data.get('joining_date'),
            company.company_name,
            company.hr_name
        )
        
        # Create offer letter record
        offer = OfferLetter(
            application_id=application_id,
            company_id=company.id,
            student_id=app.student_id,
            designation=data['designation'],
            ctc=data['ctc'],
            annual_ctc=data.get('annual_ctc'),
            job_location=data['job_location'],
            joining_date=datetime.strptime(data.get('joining_date', ''), '%Y-%m-%d').date() if data.get('joining_date') else None,
            notice_period=data.get('notice_period', 0),
            offer_content=offer_content,
            status='Generated',
            expiry_date=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(offer)
        db.session.commit()
        
        return jsonify({
            'message': 'Offer letter generated',
            'offer_id': offer.id,
            'offer': offer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def generate_offer_letter_html(student_name, designation, ctc, location, joining_date, company_name, hr_name):
    """Generate HTML content for offer letter"""
    return f"""
    <html>
    <head><style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    .letter {{ border: 1px solid #ccc; padding: 20px; }}
    .header {{ text-align: center; margin-bottom: 30px; }}
    .footer {{ margin-top: 40px; }}
    </style></head>
    <body>
    <div class="letter">
        <div class="header">
            <h2>{company_name}</h2>
            <p>Official Offer Letter</p>
        </div>
        
        <p>Dear {student_name},</p>
        
        <p>We are pleased to offer you the position of <strong>{designation}</strong> at {company_name}.</p>
        
        <table style="margin: 20px 0; width: 100%;">
            <tr><td><strong>Position:</strong></td><td>{designation}</td></tr>
            <tr><td><strong>Location:</strong></td><td>{location}</td></tr>
            <tr><td><strong>CTC:</strong></td><td>{ctc}</td></tr>
            <tr><td><strong>Joining Date:</strong></td><td>{joining_date or 'To be decided'}</td></tr>
        </table>
        
        <p>This offer is contingent upon successful background verification and fulfillment of all conditions mentioned in our discussions.</p>
        
        <p>Please confirm your acceptance within 7 days of this offer.</p>
        
        <div class="footer">
            <p>Sincerely,</p>
            <p>{hr_name}</p>
            <p>HR Department<br/>{company_name}</p>
        </div>
    </div>
    </body>
    </html>
    """


@company_bp.route('/offer/<int:offer_id>/send', methods=['POST'])
@jwt_required()
def send_offer_letter(offer_id):
    """Send offer letter to student"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        offer = OfferLetter.query.get(offer_id)
        if not offer or offer.company_id != company.id:
            return jsonify({'error': 'Offer not found'}), 404
        
        # Mark as sent (in production, actually send email)
        offer.status = 'Sent'
        offer.sent_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Offer letter sent to student',
            'offer_id': offer.id,
            'sent_date': offer.sent_date.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== HIRING ROUNDS MANAGEMENT ====================

@company_bp.route('/job/<int:job_id>/hiring-rounds', methods=['GET'])
@jwt_required()
def get_hiring_rounds(job_id):
    """Get all hiring rounds for a job"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        company = user.company
        
        job = Job.query.filter_by(id=job_id, company_id=company.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        rounds = HiringRound.query.filter_by(job_id=job_id).order_by(HiringRound.round_number).all()
        
        return jsonify([round.to_dict() for round in rounds]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@company_bp.route('/hiring-round/<int:round_id>/update-progress', methods=['POST'])
@jwt_required()
def update_round_progress(round_id):
    """Update student progress through a hiring round"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        app_round = ApplicationRound.query.get(round_id)
        if not app_round:
            return jsonify({'error': 'Round not found'}), 404
        
        app_round.status = data.get('status', app_round.status)
        app_round.score = data.get('score')
        app_round.feedback = data.get('feedback')
        
        if data.get('mark_completed'):
            app_round.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated',
            'application_round': app_round.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
