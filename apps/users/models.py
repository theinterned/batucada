from django.contrib.auth.models import User

def authenticate(username=None, password=None):
    """
    Allow model backed user objects to support authentication by
    email / password as well as username / password.
    """
    backend = 'django.contrib.auth.backends.ModelBackend'
    try:
        if '@' in username:
            kwargs = dict(email=username)
        else:
            kwargs = dict(username=username)
        user = User.objects.get(**kwargs)
        if user.check_password(password):
            user.backend = backend
            return user
    except User.DoesNotExist:
        return None
    
