"""
Session and Batch Management Routes
Purpose: Admin endpoints for managing placement sessions and academic batches
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, PlacementSession, Batch, BatchSessionMapping, Student, Job, Application
from datetime import datetime, date
from sqlalchemy import func, or_, and_

session_bp = Blueprint('session', __name__, url_prefix='/api')


def get_user_id():
    """Get user ID from JWT identity"""
    identity = get_jwt_identity()
    return int(identity) if isinstance(identity, str) else identity


def require_admin():
    """Check if current user is admin"""
    user_id = get_user_id()
    user = User.query.get(user_id)
    if not user or user.role_id != 3:
        return None
    return user


# ==================== PLACEMENT SESSION ENDPOINTS ====================

@session_bp.route('/admin/sessions', methods=['GET', 'POST'])
@jwt_required()
def manage_sessions():
    """Get all sessions or create new session (Admin only)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        if request.method == 'GET':
            # Get all sessions with statistics
            sessions = PlacementSession.query.order_by(PlacementSession.start_year.desc()).all()
            
            result = []
            for session in sessions:
                session_dict = session.to_dict()
                # Add statistics
                session_dict['job_count'] = Job.query.filter_by(session_id=session.id).count()
                session_dict['application_count'] = Application.query.filter_by(session_id=session.id).count()
                session_dict['batch_count'] = BatchSessionMapping.query.filter_by(session_id=session.id).count()
                result.append(session_dict)
            
            return jsonify(result), 200
        
        # POST - Create new session
        data = request.get_json()
        
        # Validation
        if not all(k in data for k in ['name', 'start_year', 'end_year', 'start_date', 'end_date']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check for duplicate name
        if PlacementSession.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Session with this name already exists'}), 400
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Create session
        session = PlacementSession(
            name=data['name'],
            description=data.get('description', ''),
            start_year=int(data['start_year']),
            end_year=int(data['end_year']),
            start_date=start_date,
            end_date=end_date,
            status=data.get('status', 'Upcoming'),
            created_by=admin.id
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'Placement session created successfully',
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@session_bp.route('/admin/sessions/<int:session_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def session_detail(session_id):
    """Get, update, or delete a specific session (Admin only)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        session = PlacementSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if request.method == 'GET':
            session_dict = session.to_dict()
            # Add detailed statistics
            session_dict['job_count'] = Job.query.filter_by(session_id=session.id).count()
            session_dict['application_count'] = Application.query.filter_by(session_id=session.id).count()
            
            # Get mapped batches
            mappings = BatchSessionMapping.query.filter_by(session_id=session.id).all()
            session_dict['batches'] = []
            for mapping in mappings:
                if mapping.batch:
                    batch_info = mapping.batch.to_dict()
                    batch_info['is_eligible'] = mapping.is_eligible
                    session_dict['batches'].append(batch_info)
            
            return jsonify(session_dict), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Prevent editing archived sessions' critical fields
            if session.status == 'Archived':
                allowed_fields = ['description', 'status']
                if any(k in data for k in ['name', 'start_date', 'end_date', 'start_year', 'end_year']):
                    return jsonify({'error': 'Cannot modify dates/name of archived session'}), 400
            
            # Update fields
            if 'name' in data and data['name'] != session.name:
                # Check duplicate
                if PlacementSession.query.filter_by(name=data['name']).first():
                    return jsonify({'error': 'Session name already exists'}), 400
                session.name = data['name']
            
            if 'description' in data:
                session.description = data['description']
            if 'start_year' in data:
                session.start_year = int(data['start_year'])
            if 'end_year' in data:
                session.end_year = int(data['end_year'])
            if 'start_date' in data:
                session.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            if 'end_date' in data:
                session.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            if 'status' in data:
                session.status = data['status']
            
            db.session.commit()
            return jsonify({
                'message': 'Session updated successfully',
                'session': session.to_dict()
            }), 200
        
        elif request.method == 'DELETE':
            # Prevent deletion if jobs or applications exist
            job_count = Job.query.filter_by(session_id=session.id).count()
            app_count = Application.query.filter_by(session_id=session.id).count()
            
            if job_count > 0 or app_count > 0:
                return jsonify({
                    'error': f'Cannot delete session with {job_count} jobs and {app_count} applications. Archive it instead.'
                }), 400
            
            db.session.delete(session)
            db.session.commit()
            return jsonify({'message': 'Session deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@session_bp.route('/admin/sessions/<int:session_id>/set-active', methods=['PUT'])
@jwt_required()
def set_active_session(session_id):
    """Set a session as the active session (Admin only)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        session = PlacementSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check if session can be activated
        if session.status == 'Archived':
            return jsonify({'error': 'Cannot activate an archived session'}), 400
        
        # Deactivate all other sessions
        PlacementSession.query.update({'status': 'Upcoming'})
        
        # Activate this session
        session.status = 'Active'
        db.session.commit()
        
        return jsonify({
            'message': 'Session activated successfully',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@session_bp.route('/sessions/active', methods=['GET'])
@jwt_required()
def get_active_session():
    """Get the currently active placement session (All users)"""
    try:
        session = PlacementSession.query.filter_by(status='Active').first()
        
        if not session:
            # Return default/legacy session
            session = PlacementSession.query.filter_by(is_default=True).first()
        
        if not session:
            return jsonify({'error': 'No active placement session found'}), 404
        
        return jsonify(session.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BATCH ENDPOINTS ====================

@session_bp.route('/admin/batches', methods=['GET', 'POST'])
@jwt_required()
def manage_batches():
    """Get all batches or create new batch (Admin only)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        if request.method == 'GET':
            batches = Batch.query.order_by(Batch.end_year.desc()).all()
            
            result = []
            for batch in batches:
                batch_dict = batch.to_dict()
                # Add student count
                batch_dict['student_count'] = Student.query.filter_by(batch_id=batch.id).count()
                # Add session count
                batch_dict['session_count'] = BatchSessionMapping.query.filter_by(batch_id=batch.id).count()
                result.append(batch_dict)
            
            return jsonify(result), 200
        
        # POST - Create new batch
        data = request.get_json()
        
        # Validation
        if not all(k in data for k in ['batch_code', 'start_year', 'end_year', 'degree']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check for duplicate batch_code
        if Batch.query.filter_by(batch_code=data['batch_code']).first():
            return jsonify({'error': 'Batch code already exists'}), 400
        
        # Create batch
        batch = Batch(
            batch_code=data['batch_code'],
            start_year=int(data['start_year']),
            end_year=int(data['end_year']),
            degree=data['degree'],
            program=data.get('program', ''),
            description=data.get('description', ''),
            status=data.get('status', 'Active')
        )
        
        db.session.add(batch)
        db.session.commit()
        
        return jsonify({
            'message': 'Batch created successfully',
            'batch': batch.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@session_bp.route('/admin/batches/<int:batch_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def batch_detail(batch_id):
    """Get, update, or delete a specific batch (Admin only)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        if request.method == 'GET':
            batch_dict = batch.to_dict()
            # Add detailed info
            batch_dict['students'] = [s.to_dict() for s in Student.query.filter_by(batch_id=batch.id).all()]
            
            # Get mapped sessions
            mappings = BatchSessionMapping.query.filter_by(batch_id=batch.id).all()
            batch_dict['sessions'] = []
            for mapping in mappings:
                if mapping.session:
                    session_info = mapping.session.to_dict()
                    session_info['is_eligible'] = mapping.is_eligible
                    batch_dict['sessions'].append(session_info)
            
            return jsonify(batch_dict), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Update fields
            if 'batch_code' in data and data['batch_code'] != batch.batch_code:
                if Batch.query.filter_by(batch_code=data['batch_code']).first():
                    return jsonify({'error': 'Batch code already exists'}), 400
                batch.batch_code = data['batch_code']
            
            if 'start_year' in data:
                batch.start_year = int(data['start_year'])
            if 'end_year' in data:
                batch.end_year = int(data['end_year'])
            if 'degree' in data:
                batch.degree = data['degree']
            if 'program' in data:
                batch.program = data['program']
            if 'description' in data:
                batch.description = data['description']
            if 'status' in data:
                batch.status = data['status']
            
            db.session.commit()
            return jsonify({
                'message': 'Batch updated successfully',
                'batch': batch.to_dict()
            }), 200
        
        elif request.method == 'DELETE':
            # Check if students are assigned
            student_count = Student.query.filter_by(batch_id=batch.id).count()
            if student_count > 0:
                return jsonify({
                    'error': f'Cannot delete batch with {student_count} students assigned'
                }), 400
            
            db.session.delete(batch)
            db.session.commit()
            return jsonify({'message': 'Batch deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== BATCH-SESSION MAPPING ENDPOINTS ====================

@session_bp.route('/admin/sessions/<int:session_id>/batches', methods=['POST'])
@jwt_required()
def map_batch_to_session(session_id):
    """Map a batch to a session (Admin only)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        session = PlacementSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json()
        batch_id = data.get('batch_id')
        
        if not batch_id:
            return jsonify({'error': 'batch_id is required'}), 400
        
        batch = Batch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        # Check if mapping already exists
        existing = BatchSessionMapping.query.filter_by(
            batch_id=batch_id,
            session_id=session_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Batch already mapped to this session'}), 400
        
        # Create mapping
        mapping = BatchSessionMapping(
            batch_id=batch_id,
            session_id=session_id,
            is_eligible=data.get('is_eligible', True)
        )
        
        db.session.add(mapping)
        db.session.commit()
        
        return jsonify({
            'message': 'Batch mapped to session successfully',
            'mapping': mapping.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@session_bp.route('/admin/sessions/<int:session_id>/batches/<int:batch_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_batch_session_mapping(session_id, batch_id):
    """Update or remove batch-session mapping (Admin only)"""
    try:
        admin = require_admin()
        if not admin:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403
        
        mapping = BatchSessionMapping.query.filter_by(
            batch_id=batch_id,
            session_id=session_id
        ).first()
        
        if not mapping:
            return jsonify({'error': 'Mapping not found'}), 404
        
        if request.method == 'PUT':
            data = request.get_json()
            
            if 'is_eligible' in data:
                mapping.is_eligible = bool(data['is_eligible'])
            
            db.session.commit()
            return jsonify({
                'message': 'Mapping updated successfully',
                'mapping': mapping.to_dict()
            }), 200
        
        elif request.method == 'DELETE':
            db.session.delete(mapping)
            db.session.commit()
            return jsonify({'message': 'Mapping removed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== STUDENT BATCH INFO ====================

@session_bp.route('/student/batch-info', methods=['GET'])
@jwt_required()
def get_student_batch_info():
    """Get current student's batch and eligible sessions"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if user.role_id != 1:
            return jsonify({'error': 'Unauthorized - Student access only'}), 403
        
        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        result = {
            'batch_id': student.batch_id,
            'batch_code': None,
            'eligible_sessions': []
        }
        
        if student.batch:
            result['batch_code'] = student.batch.batch_code
            result['batch_details'] = student.batch.to_dict()
            
            # Get eligible sessions for this batch
            mappings = BatchSessionMapping.query.filter_by(
                batch_id=student.batch_id,
                is_eligible=True
            ).all()
            
            for mapping in mappings:
                if mapping.session and mapping.session.status in ['Active', 'Upcoming']:
                    result['eligible_sessions'].append(mapping.session.to_dict())
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== COMPANY SESSION CONTEXT ====================

@session_bp.route('/company/sessions', methods=['GET'])
@jwt_required()
def get_company_sessions():
    """Get active and upcoming sessions for company job posting"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if user.role_id != 2:
            return jsonify({'error': 'Unauthorized - Company access only'}), 403
        
        sessions = PlacementSession.query.filter(
            PlacementSession.status.in_(['Active', 'Upcoming'])
        ).order_by(PlacementSession.start_year.desc()).all()
        
        result = []
        for session in sessions:
            session_dict = session.to_dict()
            # Add available batches for this session
            mappings = BatchSessionMapping.query.filter_by(
                session_id=session.id,
                is_eligible=True
            ).all()
            
            batches = [mapping.batch.to_dict() for mapping in mappings if mapping.batch]
            session_dict['batches'] = batches  # Frontend expects 'batches'
            session_dict['batch_count'] = len(batches)  # Frontend expects 'batch_count'
            result.append(session_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in get_company_sessions: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500
