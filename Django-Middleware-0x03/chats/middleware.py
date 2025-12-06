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
    