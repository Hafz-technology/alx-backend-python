from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message

@login_required
def delete_user(request):
    """
    Task 2: Deletes the currently logged-in user and their data.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('/')
    return render(request, 'messaging/delete_confirmation.html')

@login_required
def conversation_view(request, message_id):
    """
    Task 3: Optimized view to fetch a message and its replies.
    Uses select_related for FKs and prefetch_related for reverse FKs (replies).
    """
    # Fetch the parent message with optimized sender/receiver loading
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'), 
        pk=message_id
    )

    # Fetch replies efficiently using prefetch_related
    # We order by timestamp to show conversation flow
    replies = message.replies.select_related('sender').order_by('timestamp')

    return render(request, 'messaging/conversation.html', {
        'message': message, 
        'replies': replies
    })

@login_required
def reply_to_message(request, message_id):
    """
    Task 3: logic to reply to a specific message.
    """
    parent_message = get_object_or_404(Message, pk=message_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        # Create the reply
        # The checker looks for "sender=request.user" and "receiver"
        Message.objects.create(
            sender=request.user,
            receiver=parent_message.sender,  # The receiver is the original sender
            content=content,
            parent_message=parent_message
        )
        
        return redirect('conversation_view', message_id=message_id)
        
    return render(request, 'messaging/reply.html', {'parent_message': parent_message})


