from rest_framework import serializers
from .models import Conversation, Message, AnalyticsData
from collections import Counter
from datetime import datetime
from typing import List, Dict


class MessageSerializer(serializers.ModelSerializer):
    formated_data = serializers.SerializerMethodField()

    def get_formated_data(self, obj: Message) -> Dict[str, str]:
        return {
            "id": obj.id,
            "content": obj.content,
            "timestamp": str(obj.timestamp),
            "sender": obj.sender.lower(),
            "emotion": obj.emotion,
            "emotionConfidence": obj.emotion_confidence,
            "complianceFlags": obj.compliance_flags
        }
    
    def to_representation(self, instance: Message) -> Dict[str, str]:
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "content": data["content"],
            "timestamp": str(data["timestamp"]),
            "sender": data["sender"].lower(),
            "emotion": data["emotion"],
            "emotionConfidence": data["emotion_confidence"],
            "complianceFlags": data["compliance_flags"]
        }
    
    class Meta:
        model = Message
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    formated_data = serializers.SerializerMethodField()

    def get_formated_data(self, obj: Conversation) -> Dict[str, str]:
        return {
            "id": obj.id,
            "customerName": obj.customer_name,
            "agentName": obj.agent_name,
            "startTime": str(obj.start_time),
            "endTime": str(obj.end_time),
            "status": obj.status,
            "primaryEmotion": obj.primary_emotion,
            "messages": MessageSerializer(obj.messages.all(), many=True).data,
            "overallComplianceScore": obj.overall_compliance_score,
        }
    
    def to_representation(self, instance: Conversation) -> Dict[str, str]:
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "customerName": data["customer_name"],
            "agentName": data["agent_name"],
            "startTime": str(data["start_time"]),
            "endTime": str(data["end_time"]),
            "status": data["status"],
            "primaryEmotion": data["primary_emotion"],
            "messages": data["messages"],
            "overallComplianceScore": data["overall_compliance_score"]
        }
    
    class Meta:
        model = Conversation
        fields = '__all__'



class AnalyticsDataSerializer(serializers.Serializer):
    data = serializers.SerializerMethodField()

    def get_data(self, obj):
        conversations = obj  
        emotion_counter = Counter()
        trends = []
        total_score = 0
        total_conversations = len(conversations)

        for convo in conversations:
            total_score += convo.overall_compliance_score

            messages = convo.messages.all()
            for msg in messages:
                emotion_counter[msg.emotion] += 1

            date_str = convo.start_time.strftime('%Y-%m-%d')

            trends.append({
                "date": date_str,
                "complianceScore": convo.overall_compliance_score,
                "emotionScore": round(
                    sum(m.emotion_confidence for m in messages) / (len(messages) * 100)
                ) if messages else 0
            })

        average_score = round(total_score / total_conversations, 1) if total_conversations else 0
        compliant_percentage = round(
            (sum(1 for c in conversations if c.overall_compliance_score >= 80) / total_conversations) * 100, 1
        ) if total_conversations else 0

        return {
            "complianceOverview": {
                "totalConversations": total_conversations,
                "compliantPercentage": compliant_percentage,
                "averageScore": average_score
            },
            "emotionBreakdown": dict(emotion_counter),
            "trendsData": sorted(trends, key=lambda x: x["date"])
        }

    def to_representation(self, instance):
        data = self.get_data(instance)
        return {
            "complianceOverview": data["complianceOverview"],
            "emotionBreakdown": data["emotionBreakdown"],
            "trendsData": data["trendsData"]
        }