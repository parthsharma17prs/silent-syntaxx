"""
Learning Guide Routes - AI-Powered Personalized Roadmaps
Uses Groq's Llama 3 AI to generate personalized learning paths
"""

import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Application, Job
from groq import Groq

learning_guide_bp = Blueprint('learning_guide', __name__, url_prefix='/api/student/learning-guide')

# Initialize Groq client
def get_groq_client():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        raise Exception('Groq API key not configured. Please add your API key to .env file.')
    return Groq(api_key=api_key)

@learning_guide_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applied_companies():
    """Get all companies user has applied to with round information"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role_id != 1:
            return jsonify({'error': 'Unauthorized'}), 403
        
        student = user.student
        applications = Application.query.filter_by(student_id=student.id).all()
        
        companies_data = []
        for app in applications:
            job = app.job
            company = job.company
            
            # Calculate days until deadline or next round
            days_remaining = None
            round_info = "Application Submitted"
            
            if job.application_deadline:
                deadline = job.application_deadline
                today = datetime.now().date()
                if deadline >= today:
                    days_remaining = (deadline - today).days
                    round_info = f"Deadline in {days_remaining} days"
                else:
                    round_info = "Deadline passed"
            
            # Determine current stage
            current_stage = app.status
            if current_stage == 'Applied':
                stage_info = "Initial Application Stage"
            elif current_stage == 'Shortlisted':
                stage_info = "Shortlisted - Awaiting Interview"
            elif current_stage == 'Interview':
                stage_info = "Interview Stage"
            elif current_stage == 'Selected':
                stage_info = "Selected"
            elif current_stage == 'Rejected':
                stage_info = "Application Rejected"
            else:
                stage_info = current_stage
            
            companies_data.append({
                'application_id': app.id,
                'job_id': job.id,
                'company_name': company.company_name,
                'company_logo': company.logo_url,
                'job_title': job.title,
                'job_type': job.job_type,
                'location': job.location,
                'status': current_stage,
                'stage_info': stage_info,
                'applied_at': app.applied_at.isoformat(),
                'days_remaining': days_remaining,
                'round_info': round_info,
                'requirements': job.requirements,
                'skills_required': job.description,
                'company_industry': company.industry
            })
        
        return jsonify({
            'success': True,
            'applications': companies_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_guide_bp.route('/generate-roadmap', methods=['POST'])
@jwt_required()
def generate_learning_roadmap():
    """Generate AI-powered personalized learning roadmap"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role_id != 1:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.json
        application_id = data.get('application_id')
        
        if not application_id:
            return jsonify({'error': 'Application ID required'}), 400
        
        # Get application details
        application = Application.query.get(application_id)
        if not application or application.student_id != user.student.id:
            return jsonify({'error': 'Application not found'}), 404
        
        job = application.job
        company = job.company
        student = user.student
        
        # Calculate days remaining
        days_remaining = "Not specified"
        if job.application_deadline:
            deadline = job.application_deadline
            today = datetime.now().date()
            if deadline >= today:
                days_remaining = f"{(deadline - today).days} days"
            else:
                days_remaining = "Deadline passed"
        
        # Prepare context for AI
        student_context = f"""
Student Profile:
- Name: {student.full_name}
- Branch: {student.branch}
- CGPA: {student.cgpa}
- Current Status: {application.status}
- Skills: {student.skills if hasattr(student, 'skills') else 'Not specified'}
"""
        
        job_context = f"""
Target Company: {company.company_name}
Position: {job.title}
Job Type: {job.job_type}
Location: {job.location}
Industry: {company.industry if company.industry else 'Technology'}
Current Application Stage: {application.status}
Days Until Deadline: {days_remaining}

Job Requirements:
{job.requirements if job.requirements else 'Not specified'}

Job Description:
{job.description}

Required CGPA: {job.min_cgpa if job.min_cgpa else 'No minimum'}
Eligible Branches: {job.eligible_branches if job.eligible_branches else 'All'}
"""
        
        # Calculate number of days for roadmap
        days_num = 29  # default
        if job.application_deadline:
            deadline = job.application_deadline
            today = datetime.now().date()
            if deadline >= today:
                days_num = (deadline - today).days
        
        # Generate roadmap using Groq Llama 3
        try:
            client = get_groq_client()
            
            prompt = f"""You are an expert career counselor. Create a simple, focused learning roadmap.

{student_context}

{job_context}

Generate EXACTLY 4 sections in this format:

## 1. SKILL GAP ANALYSIS
Identify the specific skills the student is missing compared to job requirements. List each gap as a bullet point.

## 2. COMPANY REQUIREMENTS
List the key technical and soft skills this company specifically looks for. Be specific to {company.company_name}.

## 3. MAJOR TOPICS TO COVER
List the most important topics the student must study. Prioritize based on the job description.

## 4. DAY-BY-DAY ROADMAP
Create a clear day-by-day study plan from Day 1 to Day {days_num}.
Format as:
- Day 1-3: [Topic]
- Day 4-7: [Topic]
- Day 8-14: [Topic]
... and so on until Day {days_num}

Keep each section concise and actionable. Use bullet points. No lengthy paragraphs."""

            response = client.chat.completions.create(
                model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor specializing in tech placements and interview preparation. Provide detailed, actionable, and personalized guidance."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            roadmap_content = response.choices[0].message.content
            
            # Parse and structure the roadmap
            roadmap_data = {
                'success': True,
                'company_name': company.company_name,
                'company_logo': company.logo_url,
                'job_title': job.title,
                'job_type': job.job_type,
                'current_stage': application.status,
                'days_remaining': days_remaining,
                'roadmap_content': roadmap_content,
                'generated_at': datetime.now().isoformat(),
                'application_id': application_id
            }
            
            return jsonify(roadmap_data), 200
            
        except Exception as ai_error:
            return jsonify({
                'error': 'Failed to generate roadmap with AI',
                'details': str(ai_error),
                'fallback': True
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@learning_guide_bp.route('/quick-tips/<int:application_id>', methods=['GET'])
@jwt_required()
def get_quick_tips(application_id):
    """Get quick AI-generated tips for specific application"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role_id != 1:
            return jsonify({'error': 'Unauthorized'}), 403
        
        application = Application.query.get(application_id)
        if not application or application.student_id != user.student.id:
            return jsonify({'error': 'Application not found'}), 404
        
        job = application.job
        company = job.company
        
        try:
            client = get_groq_client()
            
            prompt = f"""Give 5 quick, actionable tips for a student preparing for {company.company_name}'s {job.title} position. 
Current stage: {application.status}
Make tips specific, concise (1-2 sentences each), and immediately actionable."""

            response = client.chat.completions.create(
                model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
                messages=[
                    {"role": "system", "content": "You are a concise career advisor. Give brief, actionable tips."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            tips_content = response.choices[0].message.content
            
            return jsonify({
                'success': True,
                'tips': tips_content,
                'company_name': company.company_name,
                'job_title': job.title
            }), 200
            
        except Exception as ai_error:
            return jsonify({
                'error': 'Failed to generate tips',
                'details': str(ai_error)
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
