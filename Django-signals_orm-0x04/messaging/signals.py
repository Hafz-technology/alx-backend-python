from django.dispatch import receiver
from django.utils import timezone  # Import timezone
from .models import Message, Notification, MessageHistory

from django.db.models.signals import post_delete, post_save, pre_save
from django.contrib.auth.models import User


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                # Create history record
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content
                )
                
                # Update Message fields
                instance.edited = True
                instance.edited_at = timezone.now()
                # Note: 'edited_by' is usually set in the View, not the signal, 
                # because signals don't inherently know about the 'request.user'.
                
        except Message.DoesNotExist:
            pass
        


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal to clean up all related data when a user is deleted.
    Note: If on_delete=models.CASCADE is set in models, this is redundant 
    but ensures explicit data cleanup as per task requirements.
    """
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete all messages received by the user
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications associated with the user
    Notification.objects.filter(user=instance).delete()
    

        
        
        