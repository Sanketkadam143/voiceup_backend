from rest_framework import generics
from .models import Conversation, AnalyticsData
from .serializers import ConversationSerializer, AnalyticsDataSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class ConversationListView(generics.ListAPIView):
    queryset = Conversation.objects.all().prefetch_related('messages')
    serializer_class = ConversationSerializer

class AnalyticsDataView(APIView):
    def get(self, request, *args, **kwargs):
        conversations = Conversation.objects.prefetch_related('messages').all()
        serializer = AnalyticsDataSerializer(conversations, context={'request': request})
        return Response(serializer.data, status=200)

