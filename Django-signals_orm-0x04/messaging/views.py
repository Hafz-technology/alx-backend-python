

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User



@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        # The delete() method triggers the standard Django deletion process
        # which includes cascading deletes defined in models.py
        user.delete()
        return redirect('/')  # Redirect to home or login page after deletion
    
    # If GET request, you might render a confirmation page
    return render(request, 'messaging/delete_confirmation.html')


