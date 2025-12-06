import logging
from datetime import datetime

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
    
    