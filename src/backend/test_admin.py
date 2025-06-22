#!/usr/bin/env python3
"""
Simple script to test admin access and create users
"""

import os
import sys
import django

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def create_simple_admin():
    """Create a simple admin user"""
    try:
        # Check if admin user exists
        if User.objects.filter(username='admin').exists():
            user = User.objects.get(username='admin')
            print(f"Admin user already exists:")
            print(f"  ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Is superuser: {user.is_superuser}")
            print(f"  Is staff: {user.is_staff}")
            print(f"  Is active: {user.is_active}")
            return user
        
        # Create new admin user
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        
        print(f"Created admin user:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Password: admin123")
        print(f"  Is superuser: {user.is_superuser}")
        print(f"  Is staff: {user.is_staff}")
        print(f"  Is active: {user.is_active}")
        
        return user
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return None

def list_all_users():
    """List all users in the database"""
    users = User.objects.all()
    print(f"\nAll users in database ({users.count()}):")
    for user in users:
        print(f"  - {user.username} (ID: {user.id}, Staff: {user.is_staff}, Super: {user.is_superuser})")

if __name__ == "__main__":
    print("=== Django Admin User Test ===")
    create_simple_admin()
    list_all_users()
    print("\nTry logging in with:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  URL: http://127.0.0.1:8000/admin/") 