# File: setup.py
#
# Run this file before running the project.

from sahara import bcrypt, db
from sahara.models import User
from init_books import generate_books

# Constants
ADMIN_PASSWORD = 'password'

# Reset database
print('Resetting database... ', end='')
db.drop_all()
db.create_all()
print('done.')

# Create admin user
print('Creating admin user... ', end='')
admin = User(
    email='admin@sahara.com',
    password=bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8'),
    is_subscribed=False,
    first_name='Sahara',
    last_name='Devs',
    phone_number='0123456789'
)
admin.commit_to_system()
print('done.')

print('Generating books... ')
generate_books(60)
print('done.')

print('Good to go!')
