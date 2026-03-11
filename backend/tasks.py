"""Celery tasks for background jobs - reminders, reports, CSV exports."""
import csv
import os
from datetime import datetime, date, timedelta
from celery import Celery
from celery.schedules import crontab

celery = Celery('placement_portal')


def init_celery(app):
    """Initialize Celery with Flask app context."""
    celery.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        timezone='Asia/Kolkata',
        beat_schedule={
            'daily-interview-reminders': {
                'task': 'tasks.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),  # Every day at 8 AM
            },
            'monthly-placement-report': {
                'task': 'tasks.generate_monthly_report',
                'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of every month at 9 AM
            },
        }
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders about upcoming interview deadlines and application deadlines."""
    from models import db, Application, JobPosition, Student, User
    from utils.email import send_reminder

    tomorrow = date.today() + timedelta(days=1)
    upcoming_week = date.today() + timedelta(days=7)

    # Remind students about upcoming interviews
    upcoming_interviews = Application.query.filter(
        Application.status == 'interview',
        Application.interview_date != None,
        Application.interview_date >= date.today(),
        Application.interview_date <= upcoming_week
    ).all()

    for app in upcoming_interviews:
        student = Student.query.get(app.student_id)
        job = JobPosition.query.get(app.job_id)
        if student and job and student.user:
            days_left = (app.interview_date - date.today()).days
            message = (
                f'Reminder: You have an interview for "{job.title}" at {job.company.name} '
                f'on {app.interview_date.strftime("%B %d, %Y")} '
                f'({days_left} day{"s" if days_left != 1 else ""} remaining).'
            )
            if app.interview_link:
                message += f'\nInterview Link: {app.interview_link}'
            if app.interview_time:
                message += f'\nTime: {app.interview_time}'

            send_reminder(student.user.email, 'Interview Reminder', message)

    # Remind about application deadlines
    closing_soon = JobPosition.query.filter(
        JobPosition.status == 'approved',
        JobPosition.is_active == True,
        JobPosition.application_deadline >= date.today(),
        JobPosition.application_deadline <= tomorrow + timedelta(days=2)
    ).all()

    students = Student.query.filter_by(is_blacklisted=False).all()
    for job in closing_soon:
        days_left = (job.application_deadline - date.today()).days
        for student in students:
            if student.user:
                message = (
                    f'Reminder: Application deadline for "{job.title}" at {job.company.name} '
                    f'is {job.application_deadline.strftime("%B %d, %Y")} '
                    f'({days_left} day{"s" if days_left != 1 else ""} remaining). Apply now!'
                )
                send_reminder(student.user.email, 'Application Deadline Reminder', message)

    return f'Sent reminders for {len(upcoming_interviews)} interviews and {len(closing_soon)} application deadlines'


@celery.task(name='tasks.generate_monthly_report')
def generate_monthly_report():
    """Generate monthly placement activity report and send to admin."""
    from models import db, Application, JobPosition, Placement, Company, Student, User
    from utils.email import send_email

    today = date.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    month_name = first_day_last_month.strftime('%B %Y')

    # Gather statistics
    drives_count = JobPosition.query.filter(
        JobPosition.created_at >= datetime.combine(first_day_last_month, datetime.min.time()),
        JobPosition.created_at <= datetime.combine(last_day_last_month, datetime.max.time())
    ).count()

    applications_count = Application.query.filter(
        Application.application_date >= datetime.combine(first_day_last_month, datetime.min.time()),
        Application.application_date <= datetime.combine(last_day_last_month, datetime.max.time())
    ).count()

    selections_count = Application.query.filter(
        Application.status == 'selected',
        Application.updated_at >= datetime.combine(first_day_last_month, datetime.min.time()),
        Application.updated_at <= datetime.combine(last_day_last_month, datetime.max.time())
    ).count()

    placements_count = Placement.query.filter(
        Placement.created_at >= datetime.combine(first_day_last_month, datetime.min.time()),
        Placement.created_at <= datetime.combine(last_day_last_month, datetime.max.time())
    ).count()

    new_companies = Company.query.filter(
        Company.created_at >= datetime.combine(first_day_last_month, datetime.min.time()),
        Company.created_at <= datetime.combine(last_day_last_month, datetime.max.time())
    ).count()

    new_students = Student.query.filter(
        Student.created_at >= datetime.combine(first_day_last_month, datetime.min.time()),
        Student.created_at <= datetime.combine(last_day_last_month, datetime.max.time())
    ).count()

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_placements = Placement.query.count()

    # Generate HTML report
    html_report = f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Monthly Placement Report - {month_name}</title></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f0f2f5;">
        <div style="max-width: 700px; margin: 0 auto; background: #ffffff;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 40px; text-align: center;">
                <h1 style="color: #e94560; margin: 0; font-size: 28px;">📊 Monthly Placement Report</h1>
                <p style="color: #a8a8b3; margin: 10px 0 0;">{month_name}</p>
            </div>
            <div style="padding: 30px;">
                <h2 style="color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 10px;">Summary Statistics</h2>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; font-weight: 600;">Metric</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; font-weight: 600; text-align: center;">This Month</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; font-weight: 600; text-align: center;">Total</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6;">Placement Drives Conducted</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center; color: #e94560; font-weight: bold;">{drives_count}</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{JobPosition.query.count()}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6;">Applications Received</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center; color: #e94560; font-weight: bold;">{applications_count}</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{Application.query.count()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6;">Students Selected</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center; color: #28a745; font-weight: bold;">{selections_count}</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{Application.query.filter_by(status="selected").count()}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6;">Placements Confirmed</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center; color: #28a745; font-weight: bold;">{placements_count}</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{total_placements}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6;">New Companies Registered</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{new_companies}</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{total_companies}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6;">New Students Registered</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{new_students}</td>
                        <td style="padding: 12px 16px; border: 1px solid #dee2e6; text-align: center;">{total_students}</td>
                    </tr>
                </table>
            </div>
            <div style="background: #1a1a2e; padding: 20px; text-align: center;">
                <p style="color: #888; font-size: 12px; margin: 0;">Placement Portal Application &copy; 2026 | Auto-generated Report</p>
            </div>
        </div>
    </body>
    </html>
    '''

    # Send to admin
    admin = User.query.filter_by(role='admin').first()
    if admin:
        send_email(
            admin.email,
            f'Monthly Placement Report - {month_name}',
            html_report
        )

    return f'Monthly report for {month_name} generated and sent'


@celery.task(name='tasks.export_applications_csv', bind=True)
def export_applications_csv(self, student_id, user_id):
    """Export student's application history as CSV - user triggered async job."""
    from models import db, Application, JobPosition, Company, Student, Notification

    student = Student.query.get(student_id)
    if not student:
        return 'Student not found'

    applications = Application.query.filter_by(student_id=student_id).order_by(
        Application.application_date.desc()
    ).all()

    # Create exports directory
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports')
    os.makedirs(export_dir, exist_ok=True)

    filename = f'applications_{student.roll_number or student.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(export_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Student ID', 'Student Name', 'Company Name', 'Drive Title',
            'Job Type', 'Application Date', 'Application Status',
            'Interview Date', 'Feedback', 'Salary Range'
        ])

        for app in applications:
            job = JobPosition.query.get(app.job_id)
            company = Company.query.get(job.company_id) if job else None

            writer.writerow([
                student.roll_number or student.id,
                student.name,
                company.name if company else 'N/A',
                job.title if job else 'N/A',
                job.job_type if job else 'N/A',
                app.application_date.strftime('%Y-%m-%d') if app.application_date else 'N/A',
                app.status,
                app.interview_date.strftime('%Y-%m-%d') if app.interview_date else 'N/A',
                app.feedback or 'N/A',
                f'{job.salary_min or 0} - {job.salary_max or 0}' if job else 'N/A'
            ])

    # Create notification
    notification = Notification(
        user_id=user_id,
        title='CSV Export Ready',
        message=f'Your application history has been exported successfully. File: {filename}',
        type='success',
        link=f'/api/student/export/download/{filename}'
    )
    db.session.add(notification)
    db.session.commit()

    return filepath
