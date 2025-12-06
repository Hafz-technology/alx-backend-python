from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone  # Import timezone
from .models import Message, Notification, MessageHistory

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
        
        
        
        