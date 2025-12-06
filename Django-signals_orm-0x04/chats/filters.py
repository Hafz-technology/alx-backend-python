import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter by sender's username
    sender = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains')
    
    # Filter by specific conversation ID
    conversation = django_filters.UUIDFilter(field_name='conversation__conversation_id')

    # Date range filters
    start_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'start_date', 'end_date']
        
        
        