
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

# Create your tests here.

class SignalTest(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_notification_creation(self):
        # Create a message from user1 to user2
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello World"
        )

        # Check if a notification was automatically created for user2
        notification = Notification.objects.filter(user=self.user2, message=message).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)