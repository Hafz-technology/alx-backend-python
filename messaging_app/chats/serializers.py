from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

# Get the custom User model ('chats.User')
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Handles user creation and reading user data.
    """
    class Meta:
        model = User
        # Fields to include in the serialization
        fields = (
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'role', 
            'password'
        )
        # Make password write-only so it's not returned in GET requests
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def create(self, validated_data):
        """
        Create and return a new user, using the custom manager's
        create_user method to handle password hashing.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number'),
            role=validated_data.get('role', 'guest')
        )
        return user


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    """
    # Use ReadOnlyField to display the sender's email (or username)
    # The sender itself is set in the view from (request.user)
    sender = serializers.ReadOnlyField(source='sender.email')

    class Meta:
        model = Message
        fields = ('id', 'sender', 'conversation', 'message_body', 'sent_at')
        # 'sent_at' is set automatically, so it should be read-only
        read_only_fields = ('sent_at',)


# chats/serializers.py doesn't contain: ["serializers.CharField", "serializers.SerializerMethodField()", "serializers.ValidationError"]

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Includes nested messages and participant details.
    """
    
    # Nested serializer for messages (read-only)
    # 'messages' is the related_name from the Message model's ForeignKey
    messages = MessageSerializer(many=True, read_only=True)
    
    # Nested serializer for participants (read-only)
    # This shows full user details in the conversation
    participants = UserSerializer(many=True, read_only=True)

    # Write-only field to accept a list of participant IDs on creation
    # This field will not be shown on GET requests
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        source='participants'  # Link this to the 'participants' model field
    )

    class Meta:
        model = Conversation
        fields = (
            'id', 
            'participants',      # For Read operations (nested UserSerializer)
            'participant_ids',   # For Write operations (list of UUIDs)
            'created_at', 
            'messages'           # For Read operations (nested MessageSerializer)
        )
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        """
        Custom create method to automatically add the request.user 
        to the participants list.
        """
        # 'participants' data (a list of User objects) is in validated_data 
        # thanks to 'source="participants"' on the PrimaryKeyRelatedField
        participants_data = validated_data.pop('participants')
        
        # Get the creator from the context (passed in from the view)
        creator = self.context['request'].user
        
        # Create the conversation
        conversation = Conversation.objects.create(**validated_data)
        
        # Add the creator to the list, use set to avoid duplicates
        participants_set = set(participants_data)
        participants_set.add(creator)
        
        # Set all participants
        conversation.participants.set(list(participants_set))
        
        return conversation
