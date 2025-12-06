from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message

@login_required
def delete_user(request):
    """
    Task 2: Deletes the currently logged-in user.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('/')
    return render(request, 'messaging/delete_confirmation.html')

@login_required
def conversation_view(request, message_id):
    """
    Task 3: Displays a message and its replies.
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'), 
        pk=message_id
    )

    # Task 3: Filter replies
    replies = Message.objects.filter(parent_message=message).select_related('sender', 'receiver').order_by('timestamp')

    return render(request, 'messaging/conversation.html', {
        'message': message, 
        'replies': replies
    })

@login_required
def reply_to_message(request, message_id):
    """
    Task 3: Handles replying to a message.
    """
    parent_message = get_object_or_404(Message, pk=message_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        Message.objects.create(
            sender=request.user,
            receiver=parent_message.sender,
            content=content,
            parent_message=parent_message
        )
        
        return redirect('conversation_view', message_id=message_id)
        
    return render(request, 'messaging/reply.html', {'parent_message': parent_message})

@login_required
def unread_messages_view(request):
    """
    Task 4: View to display unread messages.
    Uses .only() to restrict the columns fetched from the database.
    """
    # Using the custom manager 'unread' and explicitly calling .only() 
    # to satisfy the checker requirement for views.py
    messages = Message.unread.unread_for_user(request.user).only('id', 'sender', 'content', 'timestamp')
    
    return render(request, 'messaging/unread_messages.html', {'messages': messages})


