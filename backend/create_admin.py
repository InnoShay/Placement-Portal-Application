"""Programmatically create admin user after database initialization."""
from models import db, User


def create_admin(app):
    """Create the admin user if it doesn't already exist."""
    with app.app_context():
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@placement.com')
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')

        existing_admin = User.query.filter_by(email=admin_email, role='admin').first()
        if not existing_admin:
            admin = User(
                email=admin_email,
                role='admin',
                is_active=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f'[✓] Admin user created: {admin_email}')
        else:
            print(f'[✓] Admin user already exists: {admin_email}')
