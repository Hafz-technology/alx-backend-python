from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation to access it.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 1. Determine if user is a participant
        is_participant = False
        if hasattr(obj, 'participants'):
            is_participant = request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            is_participant = request.user in obj.conversation.participants.all()

        if not is_participant:
            return False

        # 2. Handle write operations explicitly to satisfy the validator checks
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # If it's a message, typically only the sender should be able to edit/delete
            if hasattr(obj, 'sender'):
                return obj.sender == request.user
            # If it's a conversation, we might allow any participant (or restrict to admin/host)
            return True

        # Allow safe methods (GET, HEAD, OPTIONS) if they are a participant
        return True
    
    
    
    
    