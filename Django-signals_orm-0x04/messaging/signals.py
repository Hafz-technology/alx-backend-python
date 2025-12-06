from django.db.models.signals import pre_save
# Ensure you import MessageHistory as well
from .models import Message, Notification, MessageHistory
from django.dispatch import receiver

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    # Check if the message already exists in the DB (it's an update, not a create)
    if instance.pk:
        try:
            # Fetch the old object from the database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Compare old content with the new content (instance.content)
            if old_message.content != instance.content:
                # Log the old content in history
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content
                )
                # Mark the current instance as edited
                instance.edited = True
                
        except Message.DoesNotExist:
            # Handle edge case where pk exists but object doesn't (rare)
            pass
        
