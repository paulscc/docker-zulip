#!/usr/bin/env python3
import os
import sys
import django

sys.path.append('/home/zulip/deployments/current')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')
django.setup()

from zerver.models import UserProfile

try:
    user = UserProfile.objects.filter(email='admin@zulip.localdomain', realm_id=2).first()
    if user:
        user.set_password('zulippassword123')
        user.save()
        print(f"Password updated successfully for {user.email}")
    else:
        print("User not found")
        # List all users in realm 2
        users = UserProfile.objects.filter(realm_id=2)
        for u in users:
            print(f"Found user: {u.email}")
except Exception as e:
    print(f"Error: {e}")
