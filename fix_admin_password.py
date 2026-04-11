#!/usr/bin/env python3
import os
import sys

sys.path.append('/home/zulip/deployments/current')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')

import django
django.setup()

from zerver.models import UserProfile

try:
    # Reset password for the existing admin
    user = UserProfile.objects.filter(email='admin@zulip.localdomain', realm_id=2).first()
    if user:
        user.set_password('zulippassword123')
        user.save()
        print(f'Password updated for {user.email}')
        print(f'User is active: {user.is_active}')
        print(f'Realm: {user.realm.string_id}')
    else:
        print("Admin user not found")
        
        # List all users in realm 2
        users = UserProfile.objects.filter(realm_id=2)
        print(f"Users in realm 2:")
        for u in users:
            print(f"  - {u.email} (active: {u.is_active})")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
