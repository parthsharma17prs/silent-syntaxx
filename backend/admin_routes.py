"""
Admin (TPO) Dashboard Routes
Comprehensive management and analytics endpoints for admin users
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, StudentVerification, StudentBlacklist, Department, BatchYear, Skill, PlacementStats, CompanyVisit, Student, User, Application, OfferLetter, Job
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, case
from sqlalchemy.orm import aliased
import json

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def get_user_id():
    """Convert JWT identity (string) to integer user_id"""
    identity = get_jwt_identity()
    return int(identity) if identity else None

def check_admin(user_id):
    """Verify user is admin"""
    user = User.query.get(user_id)
    return user and user.role_id == 3


@admin_bp.route('/company-progress', methods=['GET'])
@jwt_required()
def get_company_progress():
    """Company-wise placement progress for Companies tab"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403

        from models import Company

        companies = Company.query.all()
        company_ids = [c.id for c in companies]
        if not company_ids:
            return jsonify({'success': True, 'data': []}), 200

        # Job stats
        job_rows = db.session.query(
            Job.company_id.label('company_id'),
            func.count(Job.id).label('total_jobs'),
            func.sum(case((Job.status == 'Approved', 1), else_=0)).label('approved_jobs'),
            func.sum(case((Job.status == 'Pending', 1), else_=0)).label('pending_jobs'),
            func.max(Job.salary_range).label('salary_range_sample'),
        ).filter(Job.company_id.in_(company_ids)).group_by(Job.company_id).all()
        jobs_map = {r.company_id: r for r in job_rows}

        # Application stats (via join to jobs to get company_id)
        status_expr = func.lower(func.coalesce(Application.status, ''))
        app_rows = db.session.query(
            Job.company_id.label('company_id'),
            func.count(Application.id).label('total_applications'),
            func.sum(case((status_expr == 'shortlisted', 1), else_=0)).label('shortlisted'),
            func.sum(case((status_expr.in_(['interview', 'in interview']), 1), else_=0)).label('in_interview'),
            func.sum(case((status_expr == 'offered', 1), else_=0)).label('offered'),
            func.sum(case((status_expr.in_(['selected', 'hired']), 1), else_=0)).label('selected'),
            func.sum(case((status_expr == 'rejected', 1), else_=0)).label('rejected'),
        ).join(Job, Application.job_id == Job.id).filter(Job.company_id.in_(company_ids)).group_by(Job.company_id).all()
        apps_map = {r.company_id: r for r in app_rows}

        # Offer/placement stats
        offer_rows = db.session.query(
            OfferLetter.company_id.label('company_id'),
            func.count(OfferLetter.id).label('offers_made'),
            func.count(func.distinct(OfferLetter.student_id)).label('placed_students'),
            func.max(OfferLetter.annual_ctc).label('highest_package'),
        ).filter(OfferLetter.company_id.in_(company_ids)).group_by(OfferLetter.company_id).all()
        offers_map = {r.company_id: r for r in offer_rows}

        data = []
        for c in companies:
            j = jobs_map.get(c.id)
            a = apps_map.get(c.id)
            o = offers_map.get(c.id)

            data.append({
                'company_id': c.id,
                'company_name': c.company_name,
                'industry': getattr(c, 'industry', None),
                'company_website': getattr(c, 'company_website', None),
                'logo_url': getattr(c, 'logo_url', None),
                'total_jobs': int(getattr(j, 'total_jobs', 0) or 0),
                'approved_jobs': int(getattr(j, 'approved_jobs', 0) or 0),
                'pending_jobs': int(getattr(j, 'pending_jobs', 0) or 0),
                'total_applications': int(getattr(a, 'total_applications', 0) or 0),
                'shortlisted': int(getattr(a, 'shortlisted', 0) or 0),
                'in_interview': int(getattr(a, 'in_interview', 0) or 0),
                'offered': int(getattr(a, 'offered', 0) or 0),
                'selected': int(getattr(a, 'selected', 0) or 0),
                'rejected': int(getattr(a, 'rejected', 0) or 0),
                'offers_made': int(getattr(o, 'offers_made', 0) or 0),
                'placed_students': int(getattr(o, 'placed_students', 0) or 0),
                'highest_package': float(getattr(o, 'highest_package', 0) or 0),
            })

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/students/branch-counts', methods=['GET'])
@jwt_required()
def get_student_branch_counts():
    """Branch-wise registered/placed student counts (for Master Data -> Departments)."""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403

        # One offer per student (latest) to avoid double-counting
        latest_offer_subq = db.session.query(
            OfferLetter.student_id.label('student_id'),
            func.max(OfferLetter.id).label('offer_id')
        ).group_by(OfferLetter.student_id).subquery()

        # IMPORTANT:
        # Students may store branch as Department.code (e.g. "CSE") while the UI displays Department.name
        # (e.g. "Computer Science & Engineering"). Join via (code OR name) so counts match Master Data.
        rows = db.session.query(
            Department.name.label('branch'),
            Department.code.label('code'),
            func.count(Student.id).label('total_students'),
            func.sum(case((latest_offer_subq.c.offer_id.isnot(None), 1), else_=0)).label('placed_students')
        ).select_from(Department).outerjoin(
            Student,
            or_(Student.branch == Department.code, Student.branch == Department.name)
        ).outerjoin(
            latest_offer_subq,
            latest_offer_subq.c.student_id == Student.id
        ).group_by(Department.id, Department.name, Department.code).all()

        data = []
        for r in rows:
            total = int(r.total_students or 0)
            placed = int(r.placed_students or 0)
            data.append({
                'branch': r.branch,
                'code': getattr(r, 'code', None),
                'total_students': total,
                'placed_students': placed,
                'unplaced_students': max(0, total - placed)
            })

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students_list():
    """List students (optionally filtered by branch) with placement stats."""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403

        branch = request.args.get('branch')

        latest_offer_subq = db.session.query(
            OfferLetter.student_id.label('student_id'),
            func.max(OfferLetter.id).label('offer_id')
        ).group_by(OfferLetter.student_id).subquery()

        OfferLatest = aliased(OfferLetter)

        q = db.session.query(
            Student,
            User.email.label('email'),
            OfferLatest.annual_ctc.label('annual_ctc')
        ).join(User, Student.user_id == User.id).outerjoin(
            latest_offer_subq, latest_offer_subq.c.student_id == Student.id
        ).outerjoin(
            OfferLatest, OfferLatest.id == latest_offer_subq.c.offer_id
        )

        if branch:
            # Accept either Department.name or Department.code.
            dept = Department.query.filter(or_(Department.name == branch, Department.code == branch)).first()
            if dept:
                q = q.filter(or_(Student.branch == dept.name, Student.branch == dept.code))
            else:
                q = q.filter(Student.branch == branch)

        q = q.order_by(Student.full_name.asc())

        data = []
        for s, email, annual_ctc in q.all():
            package = float(annual_ctc) if annual_ctc is not None else 0
            placed = package > 0 or annual_ctc is not None
            data.append({
                'id': s.id,
                'full_name': s.full_name,
                'email': email,
                'enrollment_number': s.enrollment_number,
                'branch': s.branch,
                'cgpa': float(s.cgpa) if s.cgpa else 0,
                'placement_status': 'Placed' if placed else 'Unplaced',
                'package_lpa': package
            })

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== STUDENT VERIFICATION ENDPOINTS ====================

@admin_bp.route('/verification-queue', methods=['GET'])
@jwt_required()
def get_verification_queue():
    """Get paginated list of students pending document verification"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', 'Pending')
        
        query = StudentVerification.query
        
        if status_filter != 'All':
            query = query.filter_by(status=status_filter)
        
        # Server-side pagination
        total = query.count()
        verifications = query.order_by(StudentVerification.submitted_at.desc()).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'data': [v.to_dict() for v in verifications.items],
            'pagination': {
                'total': total,
                'pages': verifications.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/verification/<int:verification_id>/approve', methods=['POST'])
@jwt_required()
def approve_student_verification(verification_id):
    """Approve student document verification and activate account"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        verification = StudentVerification.query.get(verification_id)
        if not verification:
            return jsonify({'error': 'Verification record not found'}), 404
        
        # Update verification status
        verification.status = 'Verified'
        verification.verification_date = datetime.utcnow()
        verification.verified_by = user_id
        
        # Activate student's user account
        user = User.query.get(verification.student.user_id)
        if user:
            user.is_verified = True
            user.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f"Student {verification.student.full_name} verified successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/verification/<int:verification_id>/reject', methods=['POST'])
@jwt_required()
def reject_student_verification(verification_id):
    """Reject student documents with reason"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        rejection_reason = data.get('rejection_reason', '')
        
        verification = StudentVerification.query.get(verification_id)
        if not verification:
            return jsonify({'error': 'Verification record not found'}), 404
        
        verification.status = 'Rejected'
        verification.rejection_reason = rejection_reason
        verification.verification_date = datetime.utcnow()
        verification.verified_by = user_id
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f"Student {verification.student.full_name} rejected"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== BLACKLIST MANAGEMENT ENDPOINTS ====================

@admin_bp.route('/blacklist/students', methods=['GET'])
@jwt_required()
def get_blacklisted_students():
    """Get list of blacklisted students"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        blacklisted = StudentBlacklist.query.filter_by(is_blacklisted=True).all()
        
        return jsonify({
            'success': True,
            'data': [b.to_dict() for b in blacklisted]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/blacklist/add', methods=['POST'])
@jwt_required()
def blacklist_student():
    """Blacklist a student (freeze account)"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        student_id = data.get('student_id')
        reason = data.get('reason', '')
        severity = data.get('severity', 'Medium')
        duration_days = data.get('duration_days', None)  # If temporary
        
        # Check if already blacklisted
        existing = StudentBlacklist.query.filter_by(student_id=student_id).first()
        if existing:
            return jsonify({'error': 'Student already blacklisted'}), 400
        
        unblacklist_date = None
        if duration_days:
            unblacklist_date = datetime.utcnow() + timedelta(days=duration_days)
        
        blacklist = StudentBlacklist(
            student_id=student_id,
            is_blacklisted=True,
            reason=reason,
            severity=severity,
            blacklisted_by=user_id,
            unblacklist_date=unblacklist_date
        )
        
        db.session.add(blacklist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"Student blacklisted successfully",
            'data': blacklist.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/blacklist/remove/<int:blacklist_id>', methods=['POST'])
@jwt_required()
def remove_student_blacklist(blacklist_id):
    """Remove student from blacklist"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        blacklist = StudentBlacklist.query.get(blacklist_id)
        if not blacklist:
            return jsonify({'error': 'Blacklist record not found'}), 404
        
        blacklist.is_blacklisted = False
        blacklist.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Student removed from blacklist'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== MASTER DATA MANAGEMENT ====================

# DEPARTMENTS
@admin_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get all departments"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        departments = Department.query.all()
        return jsonify({
            'success': True,
            'data': [d.to_dict() for d in departments]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['POST'])
@jwt_required()
def add_department():
    """Add new department"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Check if exists
        if Department.query.filter_by(code=data.get('code')).first():
            return jsonify({'error': 'Department code already exists'}), 400
        
        dept = Department(
            name=data.get('name'),
            code=data.get('code'),
            description=data.get('description', ''),
            is_active=True
        )
        
        db.session.add(dept)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': dept.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@jwt_required()
def update_department(dept_id):
    """Update department"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        dept = Department.query.get(dept_id)
        if not dept:
            return jsonify({'error': 'Department not found'}), 404
        
        data = request.get_json()
        dept.name = data.get('name', dept.name)
        dept.description = data.get('description', dept.description)
        dept.is_active = data.get('is_active', dept.is_active)
        dept.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'data': dept.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# BATCH YEARS
@admin_bp.route('/batch-years', methods=['GET'])
@jwt_required()
def get_batch_years():
    """Get all batch years"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        years = BatchYear.query.all()
        return jsonify({
            'success': True,
            'data': [y.to_dict() for y in years]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/batch-years', methods=['POST'])
@jwt_required()
def add_batch_year():
    """Add new batch year"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if BatchYear.query.filter_by(year=data.get('year')).first():
            return jsonify({'error': 'Batch year already exists'}), 400
        
        year = BatchYear(
            year=data.get('year'),
            academic_session=data.get('academic_session'),
            is_active=True
        )
        
        db.session.add(year)
        db.session.commit()
        
        return jsonify({'success': True, 'data': year.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# SKILLS
@admin_bp.route('/skills', methods=['GET'])
@jwt_required()
def get_skills():
    """Get all skills"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        skills = Skill.query.all()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in skills]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/skills', methods=['POST'])
@jwt_required()
def add_skill():
    """Add new skill"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if Skill.query.filter_by(name=data.get('name')).first():
            return jsonify({'error': 'Skill already exists'}), 400
        
        skill = Skill(
            name=data.get('name'),
            category=data.get('category'),
            description=data.get('description', ''),
            is_active=True
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return jsonify({'success': True, 'data': skill.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ANALYTICS ENDPOINTS ====================

@admin_bp.route('/analytics/placement-stats', methods=['GET'])
@jwt_required()
def get_placement_stats():
    """Get current placement statistics"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get latest stats or calculate
        stats = PlacementStats.query.order_by(PlacementStats.date.desc()).first()
        
        if not stats:
            # Calculate from current data
            total_students = Student.query.count()
            
            # Count placed students (those with selected offers)
            placed_students = db.session.query(func.count(func.distinct(OfferLetter.student_id))).filter(
                OfferLetter.status.in_(['Sent', 'Accepted'])
            ).scalar() or 0
            
            unplaced = total_students - placed_students
            
            # Calculate package stats
            offers = OfferLetter.query.filter(OfferLetter.status.in_(['Sent', 'Accepted'])).all()
            packages = [float(o.annual_ctc) if o.annual_ctc else 0 for o in offers]
            
            highest_package = max(packages) if packages else 0
            average_package = sum(packages) / len(packages) if packages else 0
            
            # Department-wise stats
            dept_stats = {}
            departments = Department.query.all()
            for dept in departments:
                dept_total = Student.query.filter_by(branch=dept.name).count()
                dept_placed = db.session.query(func.count(func.distinct(OfferLetter.student_id))).join(
                    Student, OfferLetter.student_id == Student.id
                ).filter(
                    Student.branch == dept.name,
                    OfferLetter.status.in_(['Sent', 'Accepted'])
                ).scalar() or 0
                
                dept_stats[dept.name] = {
                    'total': dept_total,
                    'placed': dept_placed,
                    'placement_rate': (dept_placed / dept_total * 100) if dept_total > 0 else 0
                }
            
            stats = PlacementStats(
                date=datetime.utcnow().date(),
                total_students=total_students,
                placed_students=placed_students,
                unplaced_students=unplaced,
                highest_package=highest_package,
                average_package=average_package,
                department_stats=dept_stats,
                total_companies_visiting=Job.query.filter(Job.status == 'Approved').count()
            )
            db.session.add(stats)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': stats.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/company-visits', methods=['GET'])
@jwt_required()
def get_company_visits():
    """Get current company visits and their status"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get active company visits
        visits = CompanyVisit.query.filter(
            CompanyVisit.status.in_(['Scheduled', 'Ongoing'])
        ).order_by(CompanyVisit.visit_date.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [v.to_dict() for v in visits]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/conflict-check', methods=['GET'])
@jwt_required()
def check_scheduling_conflicts():
    """Check for conflicting company visits (same date/time)"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get all scheduled visits
        visits = CompanyVisit.query.filter(
            CompanyVisit.status.in_(['Scheduled', 'Ongoing'])
        ).all()
        
        conflicts = []
        
        # Find conflicts (visits within 2 hours on same date)
        for i, v1 in enumerate(visits):
            for v2 in visits[i+1:]:
                if not v1.visit_date or not v2.visit_date:
                    continue

                if v1.visit_date != v2.visit_date:
                    continue

                if v1.visit_time and v2.visit_time:
                    dt1 = datetime.combine(v1.visit_date, v1.visit_time)
                    dt2 = datetime.combine(v2.visit_date, v2.visit_time)
                    time_diff_hours = abs((dt1 - dt2).total_seconds() / 3600)

                    if time_diff_hours < 2:
                        conflicts.append({
                            'company1': v1.company.company_name if v1.company else None,
                            'company2': v2.company.company_name if v2.company else None,
                            'scheduled_date': v1.visit_date.isoformat(),
                            'severity': 'Critical' if time_diff_hours < 1 else 'Warning'
                        })
                else:
                    conflicts.append({
                        'company1': v1.company.company_name if v1.company else None,
                        'company2': v2.company.company_name if v2.company else None,
                        'scheduled_date': v1.visit_date.isoformat(),
                        'severity': 'Warning'
                    })
        
        return jsonify({
            'success': True,
            'conflicts_found': len(conflicts) > 0,
            'conflicts': conflicts
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/department-stats', methods=['GET'])
@jwt_required()
def get_department_stats():
    """Get placement stats by department"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        departments = Department.query.all()
        stats = []
        
        for dept in departments:
            total = Student.query.filter_by(branch=dept.name).count()
            placed = db.session.query(func.count(func.distinct(OfferLetter.student_id))).join(
                Student, OfferLetter.student_id == Student.id
            ).filter(
                Student.branch == dept.name,
                OfferLetter.status.in_(['Sent', 'Accepted'])
            ).scalar() or 0
            
            stats.append({
                'department': dept.name,
                'total_students': total,
                'placed': placed,
                'unplaced': total - placed,
                'placement_rate': (placed / total * 100) if total > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== REPORTS & EXPORT ====================

@admin_bp.route('/reports/student-data', methods=['GET'])
@jwt_required()
def export_student_data():
    """Export student data (for Excel or PDF)"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        students = Student.query.all()
        
        data = []
        for student in students:
            user = User.query.get(student.user_id)
            placed = OfferLetter.query.filter_by(student_id=student.id).first() is not None
            
            data.append({
                'enrollment_number': student.enrollment_number,
                'full_name': student.full_name,
                'email': user.email if user else '',
                'branch': student.branch,
                'cgpa': float(student.cgpa),
                'graduation_year': student.graduation_year,
                'is_placed': 'Yes' if placed else 'No',
                'profile_completed': 'Yes' if student.profile_completed else 'No'
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'total_records': len(data)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports/placement-report', methods=['GET'])
@jwt_required()
def get_placement_report():
    """Get comprehensive placement report"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Calculate all stats
        total_students = Student.query.count()
        placed_students = db.session.query(func.count(func.distinct(OfferLetter.student_id))).filter(
            OfferLetter.status.in_(['Sent', 'Accepted'])
        ).scalar() or 0
        
        offers = OfferLetter.query.filter(OfferLetter.status.in_(['Sent', 'Accepted'])).all()
        packages = [float(o.annual_ctc) if o.annual_ctc else 0 for o in offers]
        
        highest = max(packages) if packages else 0
        average = sum(packages) / len(packages) if packages else 0
        
        # Department breakdown
        dept_stats = []
        for dept in Department.query.all():
            total = Student.query.filter_by(branch=dept.name).count()
            placed = db.session.query(func.count(func.distinct(OfferLetter.student_id))).join(
                Student, OfferLetter.student_id == Student.id
            ).filter(
                Student.branch == dept.name,
                OfferLetter.status.in_(['Sent', 'Accepted'])
            ).scalar() or 0
            
            dept_stats.append({
                'department': dept.name,
                'total': total,
                'placed': placed,
                'rate': (placed / total * 100) if total > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'report': {
                'timestamp': datetime.utcnow().isoformat(),
                'total_students': total_students,
                'placed_students': placed_students,
                'unplaced_students': total_students - placed_students,
                'placement_rate': (placed_students / total_students * 100) if total_students > 0 else 0,
                'highest_package': float(highest),
                'average_package': float(average),
                'total_companies': Job.query.filter(Job.status == 'Approved').count(),
                'department_breakdown': dept_stats
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== MISSING ENDPOINTS FOR NEW ANALYTICS ====================

@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_comprehensive_analytics():
    """Get comprehensive analytics data for admin dashboard"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Calculate overall stats
        total_students = Student.query.count()
        placed_students = db.session.query(func.count(func.distinct(OfferLetter.student_id))).filter(
            OfferLetter.status.in_(['Sent', 'Accepted'])
        ).scalar() or 0
        
        placement_percentage = (placed_students / total_students * 100) if total_students > 0 else 0
        
        # Get offers data
        offers = OfferLetter.query.filter(OfferLetter.status.in_(['Sent', 'Accepted'])).all()
        packages = [float(o.annual_ctc) if o.annual_ctc else 0 for o in offers]
        
        highest_package = max(packages) if packages else 0
        average_package = sum(packages) / len(packages) if packages else 0
        
        # Get unique companies count
        total_companies = db.session.query(func.count(func.distinct(Job.company_id))).filter(
            Job.status == 'Approved'
        ).scalar() or 0
        
        # Branch-wise stats - get unique branches from students
        branch_wise_stats = []
        try:
            # First try to get from departments table
            departments = Department.query.all()
            branch_names = [dept.name for dept in departments] if departments else []
        except Exception:
            branch_names = []
        
        # If no departments, get unique branches from students
        if not branch_names:
            branch_result = db.session.query(Student.branch).distinct().all()
            branch_names = [b[0] for b in branch_result if b[0]]
        
        for branch_name in branch_names:
            total = Student.query.filter_by(branch=branch_name).count()
            if total == 0:
                continue
            placed = db.session.query(func.count(func.distinct(OfferLetter.student_id))).join(
                Student, OfferLetter.student_id == Student.id
            ).filter(
                Student.branch == branch_name,
                OfferLetter.status.in_(['Sent', 'Accepted'])
            ).scalar() or 0
            
            branch_wise_stats.append({
                'branch': branch_name,
                'total': total,
                'placed': placed,
                'percentage': (placed / total * 100) if total > 0 else 0
            })
        
        # Get all students with placement info
        students = Student.query.all()
        students_data = []
        for s in students:
            offer = OfferLetter.query.filter_by(student_id=s.id).filter(
                OfferLetter.status.in_(['Sent', 'Accepted'])
            ).first()
            
            students_data.append({
                'id': s.id,
                'full_name': s.full_name,
                'branch': s.branch,
                'cgpa': float(s.cgpa) if s.cgpa else 0,
                'placement_status': 'Placed' if offer else 'Unplaced',
                'package_lpa': float(offer.annual_ctc) if offer and offer.annual_ctc else 0
            })
        
        return jsonify({
            'success': True,
            'overall': {
                'total_students': total_students,
                'placed_students': placed_students,
                'unplaced_students': total_students - placed_students,
                'placement_percentage': round(placement_percentage, 2),
                'highest_package': round(highest_package, 2),
                'average_package': round(average_package, 2),
                'total_companies': total_companies
            },
            'branch_wise': branch_wise_stats,
            'students': students_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_all_applications():
    """Get all applications for analytics"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        applications = Application.query.all()
        
        apps_data = []
        for app in applications:
            # Get job and company details
            job = Job.query.get(app.job_id) if app.job_id else None
            student = Student.query.get(app.student_id) if app.student_id else None
            
            apps_data.append({
                'id': app.id,
                'student_id': app.student_id,
                'student_name': student.full_name if student else 'Unknown',
                'student_branch': student.branch if student else 'Unknown',
                'job_id': app.job_id,
                'job_title': job.title if job else 'Unknown',
                'company_id': job.company_id if job else None,
                'company_name': job.company.company_name if (job and job.company) else 'Unknown',
                'status': app.status or 'Applied',
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'ats_score': app.ats_score if hasattr(app, 'ats_score') else None
            })
        
        return jsonify({
            'success': True,
            'data': apps_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_all_jobs():
    """Get all jobs for analytics"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        jobs = Job.query.all()
        
        jobs_data = []
        for job in jobs:
            company = job.company if hasattr(job, 'company') else None
            
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company_id': job.company_id,
                'company_name': company.company_name if company else 'Unknown',
                'job_type': job.job_type or 'Full-Time',
                'location': job.location,
                'salary_range': job.salary_range,
                'status': job.status,
                'posted_at': job.posted_at.isoformat() if job.posted_at else None,
                'application_deadline': job.application_deadline.isoformat() if job.application_deadline else None
            })
        
        return jsonify({
            'success': True,
            'data': jobs_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_all_companies():
    """Get all companies for analytics"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        from models import Company
        companies = Company.query.all()
        
        companies_data = []
        for company in companies:
            companies_data.append({
                'id': company.id,
                'company_name': company.company_name,
                'industry': getattr(company, 'industry', None),
                'company_website': getattr(company, 'company_website', None),
                'logo_url': getattr(company, 'logo_url', None)
            })
        
        return jsonify({
            'success': True,
            'data': companies_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/pending-jobs', methods=['GET'])
@jwt_required()
def get_pending_jobs():
    """Get jobs pending admin approval"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        pending_jobs = Job.query.filter_by(status='Pending').all()
        
        jobs_data = []
        for job in pending_jobs:
            company = job.company if hasattr(job, 'company') else None
            
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company_name': company.company_name if company else 'Unknown',
                'job_type': job.job_type or 'Full-Time',
                'location': job.location,
                'salary_range': job.salary_range,
                'application_deadline': job.application_deadline.isoformat() if job.application_deadline else None,
                'posted_at': job.posted_at.isoformat() if job.posted_at else None
            })
        
        return jsonify({
            'success': True,
            'data': jobs_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/approve-job/<int:job_id>', methods=['PUT'])
@jwt_required()
def approve_or_reject_job(job_id):
    """Approve or reject a job posting"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        new_status = data.get('status')  # 'Approved' or 'Rejected'
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        job.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Job {new_status.lower()} successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/announcements', methods=['GET'])
@jwt_required()
def get_announcements():
    """Get all announcements"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        from models import Announcement
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
        
        announcements_data = []
        for ann in announcements:
            announcements_data.append({
                'id': ann.id,
                'title': ann.title,
                'message': ann.message,
                'target_role': ann.target_role if hasattr(ann, 'target_role') else None,
                'created_at': ann.created_at.isoformat() if ann.created_at else None
            })
        
        return jsonify({
            'success': True,
            'data': announcements_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/announcements', methods=['POST'])
@jwt_required()
def create_announcement():
    """Create a new announcement"""
    try:
        user_id = get_user_id()
        if not check_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        from models import Announcement
        announcement = Announcement(
            title=data.get('title'),
            message=data.get('message'),
            target_role=data.get('target_role'),
            created_by=user_id
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Announcement created successfully',
            'id': announcement.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
