"""Company routes - Profile management, job postings, application management."""
import os
from datetime import datetime, date
from flask import Blueprint, request, jsonify, g, current_app
from models import db, Company, JobPosition, Application, Student, Placement, Notification
from utils.decorators import role_required
from utils.cache import cache

company_bp = Blueprint('company', __name__)


def get_current_company():
    """Get the company profile for the current user."""
    return Company.query.filter_by(user_id=g.current_user.id).first()


# ---- Company Profile ----

@company_bp.route('/api/company/profile', methods=['GET'])
@role_required('company')
def get_profile():
    """Get company profile."""
    company = get_current_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    return jsonify({'company': company.to_dict(include_jobs=True)}), 200


@company_bp.route('/api/company/profile', methods=['PUT'])
@role_required('company')
def update_profile():
    """Update company profile."""
    company = get_current_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    data = request.get_json()

    updatable_fields = [
        'name', 'industry', 'location', 'website', 'hr_name',
        'hr_email', 'hr_phone', 'description', 'logo_url',
        'company_size', 'founded_year'
    ]

    for field in updatable_fields:
        if field in data:
            setattr(company, field, data[field])

    company.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Profile updated successfully', 'company': company.to_dict()}), 200


# ---- Job Postings ----

@company_bp.route('/api/company/jobs', methods=['GET'])
@role_required('company')
def get_jobs():
    """Get all job postings by this company."""
    company = get_current_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    if company.approval_status != 'approved':
        return jsonify({'error': 'Company is not yet approved by admin'}), 403

    status = request.args.get('status', '').strip()
    query = JobPosition.query.filter_by(company_id=company.id)

    if status:
        query = query.filter_by(status=status)

    jobs = query.order_by(JobPosition.created_at.desc()).all()

    return jsonify({
        'jobs': [j.to_dict() for j in jobs],
        'total': len(jobs)
    }), 200


@company_bp.route('/api/company/jobs', methods=['POST'])
@role_required('company')
def create_job():
    """Create a new job posting / placement drive."""
    company = get_current_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    if company.approval_status != 'approved':
        return jsonify({'error': 'Your company must be approved by admin before creating job postings'}), 403

    if company.is_blacklisted:
        return jsonify({'error': 'Your company has been blacklisted'}), 403

    data = request.get_json()

    # Validation
    required = ['title', 'description', 'application_deadline']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
        deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()
        if deadline < date.today():
            return jsonify({'error': 'Application deadline must be in the future'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    job = JobPosition(
        company_id=company.id,
        title=data['title'].strip(),
        description=data['description'].strip(),
        job_type=data.get('job_type', 'full-time').strip(),
        salary_min=float(data['salary_min']) if data.get('salary_min') else None,
        salary_max=float(data['salary_max']) if data.get('salary_max') else None,
        skills_required=data.get('skills_required', '').strip(),
        experience_required=data.get('experience_required', '').strip(),
        eligibility_branch=data.get('eligibility_branch', '').strip(),
        min_cgpa=float(data.get('min_cgpa', 0)),
        eligibility_year=int(data['eligibility_year']) if data.get('eligibility_year') else None,
        benefits=data.get('benefits', '').strip(),
        location=data.get('location', company.location or '').strip(),
        work_mode=data.get('work_mode', 'on-site').strip(),
        openings=int(data.get('openings', 1)),
        application_deadline=deadline,
        status='pending'  # Needs admin approval
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({
        'message': 'Job posting created successfully. Awaiting admin approval.',
        'job': job.to_dict()
    }), 201


@company_bp.route('/api/company/jobs/<int:job_id>', methods=['PUT'])
@role_required('company')
def update_job(job_id):
    """Update a job posting."""
    company = get_current_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first()
    if not job:
        return jsonify({'error': 'Job posting not found'}), 404

    data = request.get_json()

    updatable_fields = [
        'title', 'description', 'job_type', 'salary_min', 'salary_max',
        'skills_required', 'experience_required', 'eligibility_branch',
        'min_cgpa', 'eligibility_year', 'benefits', 'location',
        'work_mode', 'openings'
    ]

    for field in updatable_fields:
        if field in data:
            value = data[field]
            if field in ['salary_min', 'salary_max', 'min_cgpa']:
                value = float(value) if value else None
            elif field in ['eligibility_year', 'openings']:
                value = int(value) if value else None
            setattr(job, field, value)

    if 'application_deadline' in data:
        try:
            job.application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

    job.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Job posting updated', 'job': job.to_dict()}), 200


@company_bp.route('/api/company/jobs/<int:job_id>/close', methods=['PUT'])
@role_required('company')
def close_job(job_id):
    """Close a job posting."""
    company = get_current_company()
    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first()
    if not job:
        return jsonify({'error': 'Job posting not found'}), 404

    job.status = 'closed'
    job.is_active = False
    db.session.commit()

    return jsonify({'message': 'Job posting closed', 'job': job.to_dict()}), 200


@company_bp.route('/api/company/jobs/<int:job_id>', methods=['DELETE'])
@role_required('company')
def delete_job(job_id):
    """Delete a job posting."""
    company = get_current_company()
    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first()
    if not job:
        return jsonify({'error': 'Job posting not found'}), 404

    db.session.delete(job)
    db.session.commit()

    return jsonify({'message': 'Job posting deleted'}), 200


# ---- Application Management ----

@company_bp.route('/api/company/jobs/<int:job_id>/applications', methods=['GET'])
@role_required('company')
def get_applications(job_id):
    """View applications for a specific job posting."""
    company = get_current_company()
    job = JobPosition.query.filter_by(id=job_id, company_id=company.id).first()
    if not job:
        return jsonify({'error': 'Job posting not found'}), 404

    status_filter = request.args.get('status', '').strip()
    query = Application.query.filter_by(job_id=job_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    applications = query.order_by(Application.application_date.desc()).all()

    return jsonify({
        'job': job.to_dict(),
        'applications': [a.to_dict(include_details=True) for a in applications],
        'total': len(applications)
    }), 200


@company_bp.route('/api/company/applications/<int:app_id>/status', methods=['PUT'])
@role_required('company')
def update_application_status(app_id):
    """Update application status (shortlist, reject, select, etc.)."""
    company = get_current_company()
    application = Application.query.get_or_404(app_id)

    # Verify the application belongs to a job from this company
    job = JobPosition.query.get(application.job_id)
    if not job or job.company_id != company.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    new_status = data.get('status', '').strip().lower()

    valid_statuses = ['applied', 'shortlisted', 'interview', 'offer', 'selected', 'rejected']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

    application.status = new_status
    application.feedback = data.get('feedback', application.feedback)
    application.updated_at = datetime.utcnow()

    # If selected, create a placement record
    if new_status == 'selected':
        existing_placement = Placement.query.filter_by(application_id=app_id).first()
        if not existing_placement:
            placement = Placement(
                student_id=application.student_id,
                company_id=company.id,
                job_id=application.job_id,
                application_id=app_id,
                position=job.title,
                salary=data.get('salary', job.salary_max),
                joining_date=datetime.strptime(data['joining_date'], '%Y-%m-%d').date() if data.get('joining_date') else None
            )
            db.session.add(placement)

            # Mark student as placed
            student = Student.query.get(application.student_id)
            if student:
                student.is_placed = True

    # Create notification for student
    notification = Notification(
        user_id=application.student.user_id,
        title=f'Application Update: {job.title}',
        message=f'Your application for {job.title} at {company.name} has been updated to: {new_status.upper()}',
        type='info' if new_status not in ['rejected'] else 'warning',
        link=f'/student/applications/{app_id}'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': f'Application status updated to {new_status}',
        'application': application.to_dict(include_details=True)
    }), 200


@company_bp.route('/api/company/applications/<int:app_id>/interview', methods=['PUT'])
@role_required('company')
def schedule_interview(app_id):
    """Schedule an interview for a shortlisted candidate."""
    company = get_current_company()
    application = Application.query.get_or_404(app_id)

    job = JobPosition.query.get(application.job_id)
    if not job or job.company_id != company.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if not data.get('interview_date'):
        return jsonify({'error': 'Interview date is required'}), 400

    try:
        application.interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    application.interview_time = data.get('interview_time', '')
    application.interview_link = data.get('interview_link', '')
    application.interview_location = data.get('interview_location', '')
    application.interview_notes = data.get('interview_notes', '')
    application.status = 'interview'
    application.updated_at = datetime.utcnow()

    # Create notification
    notification = Notification(
        user_id=application.student.user_id,
        title=f'Interview Scheduled: {job.title}',
        message=f'An interview has been scheduled for {job.title} at {company.name} on {data["interview_date"]}',
        type='success',
        link=f'/student/applications/{app_id}'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Interview scheduled successfully',
        'application': application.to_dict(include_details=True)
    }), 200


@company_bp.route('/api/company/dashboard', methods=['GET'])
@role_required('company')
def company_dashboard():
    """Get company dashboard data."""
    company = get_current_company()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    total_jobs = company.job_positions.count()
    active_jobs = company.job_positions.filter_by(status='approved').count()
    pending_jobs = company.job_positions.filter_by(status='pending').count()
    closed_jobs = company.job_positions.filter_by(status='closed').count()

    # Get total applications across all jobs
    job_ids = [j.id for j in company.job_positions.all()]
    total_applications = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    shortlisted = Application.query.filter(
        Application.job_id.in_(job_ids), Application.status == 'shortlisted'
    ).count() if job_ids else 0
    selected = Application.query.filter(
        Application.job_id.in_(job_ids), Application.status == 'selected'
    ).count() if job_ids else 0

    total_placements = company.placements.count()

    return jsonify({
        'company': company.to_dict(),
        'stats': {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'pending_jobs': pending_jobs,
            'closed_jobs': closed_jobs,
            'total_applications': total_applications,
            'shortlisted': shortlisted,
            'selected': selected,
            'total_placements': total_placements
        }
    }), 200
