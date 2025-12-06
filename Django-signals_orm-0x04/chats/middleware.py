import logging
from datetime import datetime

import time

from django.http import JsonResponse

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configure the logging to write to a file named 'requests.log'
        logging.basicConfig(
            filename='requests.log',
            level=logging.INFO,
            format='%(message)s'
        )

    def __call__(self, request):
        # specific logic to log the user request
        user = request.user if request.user.is_authenticated else "AnonymousUser"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        
        # Write to the log file
        logging.info(log_message)

        # Proceed with the request
        response = self.get_response(request)
        return response
   
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current hour (0-23)
        current_hour = datetime.now().hour
        
        # Define allowed hours: 9 AM to 6 PM (18:00)
        # We assume the prompt meant 9 AM (09:00) to 6 PM (18:00). 
        # Access is DENIED if it is BEFORE 9 AM or AFTER/EQUAL to 6 PM.
        if current_hour < 9 or current_hour >= 18:
            return JsonResponse(
                {'error': 'Chat access is restricted to business hours (9 AM to 6 PM).'}, 
                status=403
            )

        response = self.get_response(request)
        return response
    
    
    
class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store IP request history: {'127.0.0.1': [timestamp1, timestamp2]}
        self.ip_requests = {}

    def __call__(self, request):
        # We only limit POST requests (sending messages)
        if request.method == 'POST':
            # Get IP address
            ip = request.META.get('REMOTE_ADDR')
            current_time = time.time()
            
            # Initialize list for this IP if not exists
            if ip not in self.ip_requests:
                self.ip_requests[ip] = []

            # Filter out timestamps older than 60 seconds (1 minute window)
            # We keep only requests made in the last 60 seconds
            self.ip_requests[ip] = [t for t in self.ip_requests[ip] if current_time - t < 60]

            # Check if count exceeds limit (5 requests per minute)
            if len(self.ip_requests[ip]) >= 5:
                return JsonResponse(
                    {'error': 'Rate limit exceeded. You can only send 5 messages per minute.'}, 
                    status=429 # HTTP 429 Too Many Requests
                )

            # Add current timestamp to history
            self.ip_requests[ip].append(current_time)

        response = self.get_response(request)
        return response
    

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We generally only check permissions for authenticated users
        # and usually exclude the admin site itself to prevent locking yourself out
        if request.path.startswith('/admin/'):
             return self.get_response(request)

        if request.user.is_authenticated:
            # Get the user role (default to empty string if not set)
            role = getattr(request.user, 'role', '').lower()
            
            # Allow only 'admin' or 'moderator'
            if role not in ['admin', 'moderator']:
                return JsonResponse(
                    {'error': 'Forbidden: Access denied. Requires Admin or Moderator role.'}, 
                    status=403
                )
        
        # Note: Depending on requirements, you might also want to block 
        # unauthenticated users here, or leave that to the View permissions.
        
        response = self.get_response(request)
        return response
    
    