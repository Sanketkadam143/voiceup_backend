import json
from django.core.management.base import BaseCommand
from analytics.models import Conversation, Message
from django.utils.dateparse import parse_datetime
import os
from analytics.utils import detect_emotion_with_confidence, parse_messages, calculate_compliance_score

class Command(BaseCommand):
    help = "Load mock conversation data"

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mock_data_path = os.path.abspath(os.path.join(current_dir, '..', '..','..', 'mock_data.json'))
        print(f"Loading mock data from: {mock_data_path}")
        with open(mock_data_path, 'r') as f:
            data = json.load(f)

        for conv in data:
            final_messages = parse_messages(conv["messages"])
            analyze_score = calculate_compliance_score(final_messages)
            score = analyze_score.get("score", 0)

            print(f"Compliance score for conversation {conv['customer_name']} with {len(final_messages)} messages: {score}")
            conversation = Conversation.objects.create(
                customer_name=conv["customer_name"],
                agent_name=conv["agent_name"],
                start_time=parse_datetime(conv["start_time"]),
                end_time=parse_datetime(conv["end_time"]) if conv["end_time"] else None,
                status=conv["status"],
                overall_compliance_score = score ,
            )

            for msg in conv["messages"]:
                if not msg.get("content"):
                    print(f"Skipping message with empty content in conversation {conversation.id}")
                    continue
                res = detect_emotion_with_confidence(msg["content"])
                Message.objects.create(
                    conversation=conversation,
                    content=msg["content"],
                    timestamp=parse_datetime(msg["timestamp"]),
                    sender=msg["sender"].capitalize(),
                    emotion=res["emotion"],
                    emotion_confidence=res["confidence"]
                )
                print(f"Processed message from {msg['sender']} at {msg['timestamp']}: {msg['content'][:30]}... Emotion: {res['emotion']} Confidence: {res['confidence']}")
            print(f"Loaded conversation {conversation.id} with {len(conv['messages'])} messages.")
            conversation.primary_emotion = res["emotion"]
            conversation.save()
            

        self.stdout.write(self.style.SUCCESS("Mock data loaded successfully."))
