"""Admin routes - Dashboard, company/student management, approvals."""
from flask import Blueprint, request, jsonify, g
from models import db, User, Company, Student, JobPosition, Application, Placement
from utils.decorators import role_required
from utils.cache import cache, safe_delete_memoized

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@role_required('admin')
def admin_dashboard():
    """Get admin dashboard statistics."""
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_jobs = JobPosition.query.count()
    total_applications = Application.query.count()
    total_placements = Placement.query.count()

    pending_companies = Company.query.filter_by(approval_status='pending').count()
    pending_drives = JobPosition.query.filter_by(status='pending').count()
    active_drives = JobPosition.query.filter_by(status='approved').count()

    approved_companies = Company.query.filter_by(approval_status='approved').count()
    blacklisted_companies = Company.query.filter_by(is_blacklisted=True).count()
    blacklisted_students = Student.query.filter_by(is_blacklisted=True).count()

    selected_count = Application.query.filter_by(status='selected').count()
    rejected_count = Application.query.filter_by(status='rejected').count()

    # Recent applications
    recent_applications = Application.query.order_by(
        Application.application_date.desc()
    ).limit(10).all()

    # Recent companies
    recent_companies = Company.query.order_by(
        Company.created_at.desc()
    ).limit(5).all()

    return jsonify({
        'stats': {
            'total_students': total_students,
            'total_companies': total_companies,
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'total_placements': total_placements,
            'pending_companies': pending_companies,
            'pending_drives': pending_drives,
            'active_drives': active_drives,
            'approved_companies': approved_companies,
            'blacklisted_companies': blacklisted_companies,
            'blacklisted_students': blacklisted_students,
            'selected_count': selected_count,
            'rejected_count': rejected_count
        },
        'recent_applications': [app.to_dict(include_details=True) for app in recent_applications],
        'recent_companies': [c.to_dict() for c in recent_companies]
    }), 200


# ---- Company Management ----

@admin_bp.route('/api/admin/companies', methods=['GET'])
@role_required('admin')
def get_companies():
    """List all companies with optional search and filter."""
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Company.query

    if search:
        query = query.filter(
            db.or_(
                Company.name.ilike(f'%{search}%'),
                Company.industry.ilike(f'%{search}%'),
                Company.location.ilike(f'%{search}%')
            )
        )

    if status:
        query = query.filter_by(approval_status=status)

    pagination = query.order_by(Company.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'companies': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/api/admin/companies/<int:company_id>', methods=['GET'])
@role_required('admin')
def get_company_detail(company_id):
    """Get detailed company information."""
    company = Company.query.get_or_404(company_id)
    return jsonify({'company': company.to_dict(include_jobs=True)}), 200


@admin_bp.route('/api/admin/companies/<int:company_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_company(company_id):
    """Approve a company registration."""
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'approved'
    db.session.commit()
    safe_delete_memoized(get_companies)
    return jsonify({'message': f'{company.name} has been approved', 'company': company.to_dict()}), 200


@admin_bp.route('/api/admin/companies/<int:company_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_company(company_id):
    """Reject a company registration."""
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    safe_delete_memoized(get_companies)
    return jsonify({'message': f'{company.name} has been rejected', 'company': company.to_dict()}), 200


@admin_bp.route('/api/admin/companies/<int:company_id>/blacklist', methods=['PUT'])
@role_required('admin')
def toggle_blacklist_company(company_id):
    """Toggle blacklist status for a company."""
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()

    status = 'blacklisted' if company.is_blacklisted else 'removed from blacklist'
    return jsonify({
        'message': f'{company.name} has been {status}',
        'company': company.to_dict()
    }), 200


@admin_bp.route('/api/admin/companies/<int:company_id>', methods=['DELETE'])
@role_required('admin')
def delete_company(company_id):
    """Remove a company from the system."""
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    company_name = company.name

    db.session.delete(company)
    if user:
        db.session.delete(user)
    db.session.commit()

    return jsonify({'message': f'{company_name} has been removed from the system'}), 200


# ---- Student Management ----

@admin_bp.route('/api/admin/students', methods=['GET'])
@role_required('admin')
def get_students():
    """List all students with optional search."""
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Student.query

    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f'%{search}%'),
                Student.roll_number.ilike(f'%{search}%'),
                Student.branch.ilike(f'%{search}%'),
                Student.skills.ilike(f'%{search}%')
            )
        )

    pagination = query.order_by(Student.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'students': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/api/admin/students/<int:student_id>', methods=['GET'])
@role_required('admin')
def get_student_detail(student_id):
    """Get detailed student information."""
    student = Student.query.get_or_404(student_id)
    return jsonify({'student': student.to_dict(include_applications=True)}), 200


@admin_bp.route('/api/admin/students/<int:student_id>/blacklist', methods=['PUT'])
@role_required('admin')
def toggle_blacklist_student(student_id):
    """Toggle blacklist status for a student."""
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted

    # Also deactivate/activate user account
    user = User.query.get(student.user_id)
    if user:
        user.is_active = not student.is_blacklisted

    db.session.commit()

    status = 'blacklisted' if student.is_blacklisted else 'removed from blacklist'
    return jsonify({
        'message': f'{student.name} has been {status}',
        'student': student.to_dict()
    }), 200


@admin_bp.route('/api/admin/students/<int:student_id>/deactivate', methods=['PUT'])
@role_required('admin')
def toggle_deactivate_student(student_id):
    """Toggle active status for a student."""
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    if user:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'message': f'{student.name} has been {status}',
            'student': student.to_dict()
        }), 200
    return jsonify({'error': 'User not found'}), 404


# ---- Drive/Job Management ----

@admin_bp.route('/api/admin/drives', methods=['GET'])
@role_required('admin')
def get_all_drives():
    """List all placement drives with optional filter."""
    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = JobPosition.query

    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            db.or_(
                JobPosition.title.ilike(f'%{search}%'),
                JobPosition.location.ilike(f'%{search}%'),
                JobPosition.skills_required.ilike(f'%{search}%')
            )
        )

    pagination = query.order_by(JobPosition.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'drives': [d.to_dict(include_company=True) for d in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/api/admin/drives/<int:drive_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_drive(drive_id):
    """Approve a placement drive."""
    drive = JobPosition.query.get_or_404(drive_id)
    drive.status = 'approved'
    db.session.commit()
    return jsonify({'message': f'Drive "{drive.title}" has been approved', 'drive': drive.to_dict(include_company=True)}), 200


@admin_bp.route('/api/admin/drives/<int:drive_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_drive(drive_id):
    """Reject a placement drive."""
    drive = JobPosition.query.get_or_404(drive_id)
    drive.status = 'rejected'
    db.session.commit()
    return jsonify({'message': f'Drive "{drive.title}" has been rejected', 'drive': drive.to_dict(include_company=True)}), 200


@admin_bp.route('/api/admin/drives/<int:drive_id>/close', methods=['PUT'])
@role_required('admin')
def close_drive(drive_id):
    """Close a placement drive."""
    drive = JobPosition.query.get_or_404(drive_id)
    drive.status = 'closed'
    drive.is_active = False
    db.session.commit()
    return jsonify({'message': f'Drive "{drive.title}" has been closed', 'drive': drive.to_dict(include_company=True)}), 200


@admin_bp.route('/api/admin/drives/<int:drive_id>', methods=['DELETE'])
@role_required('admin')
def delete_drive(drive_id):
    """Delete a placement drive."""
    drive = JobPosition.query.get_or_404(drive_id)
    title = drive.title
    db.session.delete(drive)
    db.session.commit()
    return jsonify({'message': f'Drive "{title}" has been deleted'}), 200


# ---- Application Management ----

@admin_bp.route('/api/admin/applications', methods=['GET'])
@role_required('admin')
def get_all_applications():
    """List all applications."""
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Application.query

    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Application.application_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'applications': [a.to_dict(include_details=True) for a in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/api/admin/placements', methods=['GET'])
@role_required('admin')
def get_all_placements():
    """List all placements."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Placement.query.order_by(Placement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'placements': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200
