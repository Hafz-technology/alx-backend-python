from django.db import models

class UnreadMessagesManager(models.Manager):
    """
    Task 4: Custom manager to filter unread messages for a specific user.
    """
    def unread_for_user(self, user):
        # Filters messages where the receiver is the user and read is False
        # Uses .only() to optimize database load by fetching only necessary fields
        return self.get_queryset().filter(
            receiver=user, 
            read=False
        ).only('id', 'sender', 'content', 'timestamp')
        
        
        
        