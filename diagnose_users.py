#!/usr/bin/env python3
import os
import sys

sys.path.append('/home/zulip/deployments/current')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')

import django
django.setup()

from zerver.models import UserProfile, Realm

try:
    print("=== REALMS ===")
    realms = Realm.objects.all()
    for realm in realms:
        print(f"Realm {realm.id}: {realm.string_id} ({realm.name}) - {realm.domain}")
    
    print("\n=== USERS IN REALM 2 ===")
    users = UserProfile.objects.filter(realm_id=2)
    for user in users:
        print(f"User: {user.email}")
        print(f"  Active: {user.is_active}")
        print(f"  Has password: {bool(user.password)}")
        print(f"  Auth method: {getattr(user, 'auth_method', 'Unknown')}")
        print(f"  Is admin: {user.is_realm_admin}")
        print()
    
    # Try to reset password for newadmin@example.com
    user = UserProfile.objects.filter(email='newadmin@example.com', realm_id=2).first()
    if user:
        print(f"=== RESETING PASSWORD FOR {user.email} ===")
        user.set_password('zulippassword123')
        user.save()
        print("Password set successfully")
        
        # Verify password
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='newadmin@example.com', password='zulippassword123', realm=user.realm)
        print(f"Authentication test: {'SUCCESS' if auth_user else 'FAILED'}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
