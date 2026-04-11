#!/usr/bin/env python3
import os
import sys

sys.path.append('/home/zulip/deployments/current')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')

import django
django.setup()

from zerver.models import UserProfile
from django.core.cache import cache

try:
    user = UserProfile.objects.filter(email='admin@example.com', realm_id=2).first()
    if user:
        # Clear login attempts from cache
        cache.delete(f'login_attempts_{user.id}')
        print(f'Login attempts cleared for user {user.email}')
        
        # Also clear any rate limiting
        cache.delete(f'rate_limit_login_{user.email}')
        print(f'Rate limit cleared for {user.email}')
    else:
        print("User not found")
        
        # List all users in realm 2
        users = UserProfile.objects.filter(realm_id=2)
        print(f"Users in realm 2:")
        for u in users:
            print(f"  - {u.email}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
