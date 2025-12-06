from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_page # Import cache_page
from .models import Message

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('/')
    return render(request, 'messaging/delete_confirmation.html')

@login_required
@cache_page(60) # Task 5: Cache this view for 60 seconds
def conversation_view(request, message_id):
    """
    Task 3: Displays a message and its replies.
    Task 5: Cached for 60 seconds.
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'), 
        pk=message_id
    )

    replies = Message.objects.filter(parent_message=message).select_related('sender', 'receiver').order_by('timestamp')

    return render(request, 'messaging/conversation.html', {
        'message': message, 
        'replies': replies
    })

@login_required
def reply_to_message(request, message_id):
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
    messages = Message.unread.unread_for_user(request.user).only('id', 'sender', 'content', 'timestamp')
    return render(request, 'messaging/unread_messages.html', {'messages': messages})



