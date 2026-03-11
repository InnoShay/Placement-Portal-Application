"""Flask Application Factory - Placement Portal Application V2."""
import os
from flask import Flask, send_from_directory, jsonify, request, g, send_file
from flask_cors import CORS
from config import Config
from models import db
from create_admin import create_admin
from utils.cache import init_cache, cache
from utils.email import init_mail
from tasks import celery, init_celery, export_applications_csv


def create_app():
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        static_folder='../frontend/src',
        template_folder='../frontend/src'
    )
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    init_cache(app)
    init_mail(app)
    init_celery(app)

    # Create upload and export directories
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(app.config.get('EXPORT_FOLDER', 'exports'), exist_ok=True)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    # ---- Additional API Routes ----

    @app.route('/api/student/export/csv', methods=['POST'])
    def trigger_csv_export():
        """Trigger async CSV export of student applications."""
        from utils.decorators import token_required
        import jwt

        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token'}), 401

        if not token:
            return jsonify({'error': 'Token required'}), 401

        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            from models import User, Student
            user = User.query.get(payload['user_id'])
            if not user or user.role != 'student':
                return jsonify({'error': 'Unauthorized'}), 403
            student = Student.query.filter_by(user_id=user.id).first()
            if not student:
                return jsonify({'error': 'Student not found'}), 404

            task = export_applications_csv.delay(student.id, user.id)
            return jsonify({
                'message': 'CSV export started. You will be notified when ready.',
                'task_id': task.id
            }), 202
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/student/export/download/<filename>', methods=['GET'])
    def download_csv(filename):
        """Download exported CSV file."""
        export_dir = app.config.get('EXPORT_FOLDER', 'exports')
        filepath = os.path.join(export_dir, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        return jsonify({'error': 'File not found'}), 404

    @app.route('/api/notifications', methods=['GET'])
    def get_user_notifications():
        """Get notifications for current user (any role)."""
        import jwt as pyjwt
        from models import Notification

        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token'}), 401

        if not token:
            return jsonify({'error': 'Token required'}), 401

        try:
            payload = pyjwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            notifications = Notification.query.filter_by(
                user_id=payload['user_id']
            ).order_by(Notification.created_at.desc()).limit(50).all()

            return jsonify({
                'notifications': [n.to_dict() for n in notifications],
                'unread_count': sum(1 for n in notifications if not n.is_read)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ---- Frontend Routes ----

    @app.route('/')
    def index():
        """Serve the main SPA entry point."""
        from flask import render_template
        return render_template('index.html')

    @app.route('/components/<path:filename>')
    def serve_component(filename):
        """Serve Vue component files."""
        components_dir = os.path.join(app.static_folder, 'components')
        return send_from_directory(components_dir, filename)

    @app.route('/assets/<path:filename>')
    def serve_asset(filename):
        """Serve static assets."""
        assets_dir = os.path.join(app.static_folder, 'assets')
        return send_from_directory(assets_dir, filename)

    # Create database tables and admin user
    with app.app_context():
        db.create_all()
        create_admin(app)

    return app


# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
