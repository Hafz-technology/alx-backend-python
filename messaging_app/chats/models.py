import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


# --- User Model Management ---

class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin') # Set default role for superuser

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


# --- Models ---

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model extending AbstractBaseUser.
    Uses UUID for Primary Key and Email for login.
    """
    class Role(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'

    # 'user_id' from schema is mapped to 'id' (Django convention)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST,
        null=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    # Required fields for Django's auth system
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 

    # Link to the custom manager
    objects = CustomUserManager()

    # Set email as the login field
    USERNAME_FIELD = 'email'
    # 'first_name' and 'last_name' are required for createsuperuser
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class Conversation(models.Model):
    """
    Tracks a conversation between two or more users.
    """
    # 'conversation_id' from schema is mapped to 'id'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 'participants_id' from schema is a ManyToMany relationship
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"


class Message(models.Model):
    """
    A single message sent by a user within a conversation.
    """
    # 'message_id' from schema is mapped to 'id'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 'sender_id' from schema
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    # Link message to a conversation
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    message_body = models.TextField(blank=False, null=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Order messages by when they were sent
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender} at {self.sent_at}"

