from zerver.models import UserProfile

user = UserProfile.objects.filter(email='admin@zulip.localdomain', realm_id=2).first()
if user:
    user.set_password('zulippassword123')
    user.save()
    print(f'Password updated for {user.email}')
else:
    print("Admin user not found")
