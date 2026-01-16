"""
Hiring Rounds Management API Routes
Production-level endpoints for configuring recruitment workflows
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, HiringRound, RoundCandidateProgress, Job, Company, Application
from sqlalchemy import and_, or_
from datetime import datetime
import json

hiring_rounds_bp = Blueprint('hiring_rounds', __name__, url_prefix='/api/company/hiring-rounds')


def get_company_id_from_jwt():
    """Extract company ID from JWT token"""
    user_id = int(get_jwt_identity())
    from models import User
    user = User.query.get(user_id)
    if not user or user.role_id != 2:
        return None
    company = Company.query.filter_by(user_id=user_id).first()
    return company.id if company else None


def verify_job_ownership(job_id, company_id):
    """Verify that the job belongs to the company"""
    job = Job.query.filter_by(id=job_id, company_id=company_id).first()
    return job is not None


# ==================== ROUND CONFIGURATION ENDPOINTS ====================

@hiring_rounds_bp.route('/job/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_rounds(job_id):
    """
    Get all hiring rounds for a specific job
    Returns rounds in order with their configurations
    """
    try:
        company_id = get_company_id_from_jwt()
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Verify job ownership
        if not verify_job_ownership(job_id, company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Fetch all rounds for this job, ordered by round_number
        rounds = HiringRound.query.filter_by(job_id=job_id).order_by(HiringRound.round_number).all()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'rounds': [round.to_dict() for round in rounds],
            'total_rounds': len(rounds)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hiring_rounds_bp.route('/job/<int:job_id>', methods=['POST'])
@jwt_required()
def create_or_update_rounds(job_id):
    """
    Create or update hiring rounds for a job
    Accepts array of rounds and handles atomic save
    
    Expected payload:
    {
        "rounds": [
            {
                "round_number": 1,
                "round_name": "Online Assessment",
                "round_type": "Online",
                "round_mode": "MCQ",
                "description": "...",
                "duration_minutes": 60,
                "evaluation_criteria": "[{...}]",
                "is_elimination_round": true,
                ...
            }
        ]
    }
    """
    try:
        company_id = get_company_id_from_jwt()
        print(f"[DEBUG] Company ID from JWT: {company_id}")
        
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Verify job ownership
        job = Job.query.filter_by(id=job_id, company_id=company_id).first()
        if not job:
            print(f"[DEBUG] Job not found: job_id={job_id}, company_id={company_id}")
            return jsonify({'error': 'Job not found or access denied'}), 404
        
        print(f"[DEBUG] Job found: {job.title}")
        
        data = request.get_json()
        rounds_data = data.get('rounds', [])
        
        print(f"[DEBUG] Received {len(rounds_data)} rounds")
        print(f"[DEBUG] Rounds data: {rounds_data}")
        
        if not rounds_data:
            return jsonify({'error': 'No rounds provided'}), 400
        
        # Validation
        errors = validate_rounds_data(rounds_data)
        if errors:
            print(f"[DEBUG] Validation errors: {errors}")
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        print(f"[DEBUG] Validation passed")
        
        # Begin transaction - delete existing rounds and create new ones
        # This ensures consistency and handles reordering
        existing_count = HiringRound.query.filter_by(job_id=job_id).count()
        print(f"[DEBUG] Deleting {existing_count} existing rounds")
        HiringRound.query.filter_by(job_id=job_id).delete()
        
        created_rounds = []
        for round_data in rounds_data:
            print(f"[DEBUG] Creating round: {round_data.get('round_name')}")
            new_round = HiringRound(
                job_id=job_id,
                round_number=round_data.get('round_number'),
                round_name=round_data.get('round_name'),
                round_type=round_data.get('round_type', 'Online'),
                round_mode=round_data.get('round_mode'),
                description=round_data.get('description'),
                duration_minutes=round_data.get('duration_minutes'),
                evaluation_criteria=json.dumps(round_data.get('evaluation_criteria')) if round_data.get('evaluation_criteria') else None,
                is_elimination_round=round_data.get('is_elimination_round', True),
                scheduled_date=datetime.strptime(round_data['scheduled_date'], '%Y-%m-%d').date() if round_data.get('scheduled_date') else None,
                scheduled_time=datetime.strptime(round_data['scheduled_time'], '%H:%M').time() if round_data.get('scheduled_time') else None,
                venue=round_data.get('venue'),
                status=round_data.get('status', 'Draft'),
                min_passing_score=round_data.get('min_passing_score'),
                max_score=round_data.get('max_score', 100.00),
                configuration=json.dumps(round_data.get('configuration')) if round_data.get('configuration') else None,
                created_by=int(get_jwt_identity())
            )
            db.session.add(new_round)
            created_rounds.append(new_round)
        
        print(f"[DEBUG] Committing {len(created_rounds)} rounds to database")
        db.session.commit()
        print(f"[DEBUG] Commit successful!")
        
        return jsonify({
            'success': True,
            'message': f'Successfully saved {len(created_rounds)} rounds',
            'rounds': [round.to_dict() for round in created_rounds]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@hiring_rounds_bp.route('/round/<int:round_id>', methods=['PUT'])
@jwt_required()
def update_single_round(round_id):
    """
    Update a specific hiring round
    """
    try:
        company_id = get_company_id_from_jwt()
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        round_obj = HiringRound.query.get(round_id)
        if not round_obj:
            return jsonify({'error': 'Round not found'}), 404
        
        # Verify job ownership
        if not verify_job_ownership(round_obj.job_id, company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'round_name' in data:
            round_obj.round_name = data['round_name']
        if 'round_type' in data:
            round_obj.round_type = data['round_type']
        if 'round_mode' in data:
            round_obj.round_mode = data['round_mode']
        if 'description' in data:
            round_obj.description = data['description']
        if 'duration_minutes' in data:
            round_obj.duration_minutes = data['duration_minutes']
        if 'evaluation_criteria' in data:
            round_obj.evaluation_criteria = json.dumps(data['evaluation_criteria'])
        if 'is_elimination_round' in data:
            round_obj.is_elimination_round = data['is_elimination_round']
        if 'scheduled_date' in data:
            round_obj.scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date() if data['scheduled_date'] else None
        if 'scheduled_time' in data:
            round_obj.scheduled_time = datetime.strptime(data['scheduled_time'], '%H:%M').time() if data['scheduled_time'] else None
        if 'venue' in data:
            round_obj.venue = data['venue']
        if 'status' in data:
            round_obj.status = data['status']
        if 'min_passing_score' in data:
            round_obj.min_passing_score = data['min_passing_score']
        if 'max_score' in data:
            round_obj.max_score = data['max_score']
        if 'configuration' in data:
            round_obj.configuration = json.dumps(data['configuration'])
        
        round_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Round updated successfully',
            'round': round_obj.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@hiring_rounds_bp.route('/round/<int:round_id>', methods=['DELETE'])
@jwt_required()
def delete_round(round_id):
    """
    Delete a specific hiring round
    """
    try:
        company_id = get_company_id_from_jwt()
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        round_obj = HiringRound.query.get(round_id)
        if not round_obj:
            return jsonify({'error': 'Round not found'}), 404
        
        # Verify job ownership
        if not verify_job_ownership(round_obj.job_id, company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        job_id = round_obj.job_id
        db.session.delete(round_obj)
        
        # Reorder remaining rounds
        remaining_rounds = HiringRound.query.filter_by(job_id=job_id).order_by(HiringRound.round_number).all()
        for idx, r in enumerate(remaining_rounds, start=1):
            r.round_number = idx
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Round deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@hiring_rounds_bp.route('/job/<int:job_id>/reorder', methods=['POST'])
@jwt_required()
def reorder_rounds(job_id):
    """
    Reorder hiring rounds for a job
    
    Expected payload:
    {
        "round_ids": [3, 1, 2, 4]  // New order of round IDs
    }
    """
    try:
        company_id = get_company_id_from_jwt()
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if not verify_job_ownership(job_id, company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        round_ids = data.get('round_ids', [])
        
        if not round_ids:
            return jsonify({'error': 'No round IDs provided'}), 400
        
        # Update round numbers based on new order
        for new_number, round_id in enumerate(round_ids, start=1):
            round_obj = HiringRound.query.filter_by(id=round_id, job_id=job_id).first()
            if round_obj:
                round_obj.round_number = new_number
        
        db.session.commit()
        
        # Return updated rounds
        rounds = HiringRound.query.filter_by(job_id=job_id).order_by(HiringRound.round_number).all()
        
        return jsonify({
            'success': True,
            'message': 'Rounds reordered successfully',
            'rounds': [r.to_dict() for r in rounds]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== CANDIDATE PROGRESS ENDPOINTS ====================

@hiring_rounds_bp.route('/round/<int:round_id>/candidates', methods=['GET'])
@jwt_required()
def get_round_candidates(round_id):
    """
    Get all candidates in a specific round with their progress
    """
    try:
        company_id = get_company_id_from_jwt()
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        round_obj = HiringRound.query.get(round_id)
        if not round_obj:
            return jsonify({'error': 'Round not found'}), 404
        
        if not verify_job_ownership(round_obj.job_id, company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all candidate progress for this round
        candidates = RoundCandidateProgress.query.filter_by(round_id=round_id).all()
        
        # Get statistics
        total = len(candidates)
        passed = len([c for c in candidates if c.status == 'Passed'])
        failed = len([c for c in candidates if c.status == 'Failed'])
        pending = len([c for c in candidates if c.status in ['Pending', 'Invited']])
        
        return jsonify({
            'success': True,
            'round_id': round_id,
            'round_name': round_obj.round_name,
            'statistics': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'pending': pending
            },
            'candidates': [c.to_dict() for c in candidates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hiring_rounds_bp.route('/round/<int:round_id>/invite-candidates', methods=['POST'])
@jwt_required()
def invite_candidates_to_round(round_id):
    """
    Invite candidates to a specific round
    Creates progress tracking entries for selected applications
    
    Expected payload:
    {
        "application_ids": [1, 2, 3, ...]
    }
    """
    try:
        company_id = get_company_id_from_jwt()
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        round_obj = HiringRound.query.get(round_id)
        if not round_obj:
            return jsonify({'error': 'Round not found'}), 404
        
        if not verify_job_ownership(round_obj.job_id, company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        application_ids = data.get('application_ids', [])
        
        if not application_ids:
            return jsonify({'error': 'No application IDs provided'}), 400
        
        invited_count = 0
        for app_id in application_ids:
            # Check if already invited
            existing = RoundCandidateProgress.query.filter_by(
                round_id=round_id,
                application_id=app_id
            ).first()
            
            if not existing:
                application = Application.query.get(app_id)
                if application:
                    progress = RoundCandidateProgress(
                        round_id=round_id,
                        application_id=app_id,
                        student_id=application.student_id,
                        status='Invited',
                        invited_at=datetime.utcnow()
                    )
                    db.session.add(progress)
                    invited_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully invited {invited_count} candidates',
            'invited_count': invited_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@hiring_rounds_bp.route('/progress/<int:progress_id>', methods=['PUT'])
@jwt_required()
def update_candidate_progress(progress_id):
    """
    Update candidate progress in a round (scores, status, feedback)
    """
    try:
        company_id = get_company_id_from_jwt()
        if not company_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        progress = RoundCandidateProgress.query.get(progress_id)
        if not progress:
            return jsonify({'error': 'Progress record not found'}), 404
        
        # Verify ownership through round -> job -> company
        if not verify_job_ownership(progress.round.job_id, company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'status' in data:
            progress.status = data['status']
        if 'score' in data:
            progress.score = data['score']
        if 'candidate_rank' in data:
            progress.candidate_rank = data['candidate_rank']
        if 'evaluator_notes' in data:
            progress.evaluator_notes = data['evaluator_notes']
        if 'evaluation_metrics' in data:
            progress.evaluation_metrics = json.dumps(data['evaluation_metrics'])
        if 'strengths' in data:
            progress.strengths = data['strengths']
        if 'areas_of_improvement' in data:
            progress.areas_of_improvement = data['areas_of_improvement']
        
        # Update timestamps based on status
        if data.get('status') == 'In Progress' and not progress.started_at:
            progress.started_at = datetime.utcnow()
        elif data.get('status') in ['Completed', 'Passed', 'Failed']:
            if not progress.completed_at:
                progress.completed_at = datetime.utcnow()
            if 'score' in data or 'evaluator_notes' in data:
                progress.evaluated_at = datetime.utcnow()
        
        progress.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== HELPER FUNCTIONS ====================

def validate_rounds_data(rounds_data):
    """Validate rounds configuration data"""
    errors = []
    
    valid_round_types = ['Online', 'Offline']
    valid_round_modes = ['MCQ', 'Coding', 'Interview', 'Group Discussion', 'Assignment', 'Case Study', 'Presentation', 'Other']
    valid_statuses = ['Draft', 'Active', 'Completed', 'Cancelled']
    
    for idx, round_data in enumerate(rounds_data):
        round_errors = {}
        
        # Required fields
        if not round_data.get('round_number'):
            round_errors['round_number'] = 'Round number is required'
        if not round_data.get('round_name'):
            round_errors['round_name'] = 'Round name is required'
        if not round_data.get('round_mode'):
            round_errors['round_mode'] = 'Round mode is required'
        
        # Validate enums
        if round_data.get('round_type') and round_data['round_type'] not in valid_round_types:
            round_errors['round_type'] = f'Invalid round type. Must be one of: {", ".join(valid_round_types)}'
        if round_data.get('round_mode') and round_data['round_mode'] not in valid_round_modes:
            round_errors['round_mode'] = f'Invalid round mode. Must be one of: {", ".join(valid_round_modes)}'
        if round_data.get('status') and round_data['status'] not in valid_statuses:
            round_errors['status'] = f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
        
        # Validate numeric fields
        if round_data.get('duration_minutes') and (not isinstance(round_data['duration_minutes'], int) or round_data['duration_minutes'] <= 0):
            round_errors['duration_minutes'] = 'Duration must be a positive integer'
        
        if round_errors:
            errors.append({f'round_{idx + 1}': round_errors})
    
    return errors if errors else None
