from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # Task 1: Add edited field
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

class MessageHistory(models.Model):
    # Task 1: History model to store old content
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Message {self.message.id} at {self.timestamp}"

class Notification(models.Model):
    # Task 0: Notification model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}: New message from {self.message.sender}"
    
    
    