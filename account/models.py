from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from friend.models import FriendList


# Create your models here.


class MyAccountManager(BaseUserManager):
    def create_user(self, email, name,university_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        else:
            college_email = email.split('.')[-2:]
            if not (college_email == ['edu', 'in']):
                raise ValueError('Email must ends with .edu.in')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            university_name=university_name,
            
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name,university_name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            name=name,
            university_name=university_name,
           
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email",
                              max_length=100, unique=True, null=False)
    name = models.CharField(max_length=100, default='Stranger')
    university_name = models.CharField(max_length=100, default='Unknown')
    origin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','university_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

@receiver(post_save, sender=Account)
def _post_save_receiver(sender, instance, **kwargs):
	chat = FriendList.objects.get_or_create(user=instance)