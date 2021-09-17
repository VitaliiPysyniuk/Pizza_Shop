from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_kwargs):
        extra_kwargs.setdefault('role', 'manager')
        extra_kwargs.setdefault('is_active', True)

        if extra_kwargs.get('role') != 'manager':
            raise ValueError('User role has to be \'manager\'.')
        if extra_kwargs.get('is_active') is not True:
            raise ValueError('User has to be active.')
        return self.create_user(email, password, **extra_kwargs)

