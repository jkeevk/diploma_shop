import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    
    admin_data = {
        'email': 'admin@admin.com',
        'password': 'admin',
        'username': 'admin',
        'first_name': 'Admin',
        'last_name': 'Admin',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
    
    if not User.objects.filter(email=admin_data['email']).exists():
        User.objects.create_superuser(**admin_data)
        print('✓ Superuser created')
    else:
        print('✓ Superuser already exists')

if __name__ == '__main__':
    create_admin()