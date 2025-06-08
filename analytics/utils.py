from openai import OpenAI
import re
import os
from analytics.constants import COMPLIANCE_RULES, EMOTIONS
from config.settings import config


def parse_messages(messages):
    """
    parse message to a format suitable for the OpenAI API.
    """
    msg = []

    for m in messages:
        if not m.get("content"):
            print(f"Skipping message with empty content: {m}")
            continue
        msg.append({
            "sender": m["sender"].lower(),
            "text": m["content"]
        })
        
    return msg

def detect_emotion_with_confidence(user_text):
    system_prompt = (
        "You are an assistant that classifies emotional tone from customer support messages. "
        "Given a message, respond with only the detected emotion and a confidence score "
        "in percentage from the following list:\n"
        f"{', '.join(EMOTIONS)}.\n"
        "Format your response exactly as:\n"
        "Emotion: <emotion>\n"
        "Confidence: <percentage>"
    )

    try:
        client = OpenAI(
            api_key=config.get('OPENAI_API_KEY')
        )
        resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_text}
            ],
            temperature=0.2,
            max_tokens=50
        )

        content = resp.choices[0].message.content.strip()

        emotion_m = re.search(r'^Emotion:\s*(\w+)', content, re.IGNORECASE | re.MULTILINE)
        conf_m = re.search(r'^Confidence:\s*([\d.]+)', content, re.IGNORECASE | re.MULTILINE)

        emotion = emotion_m.group(1).lower() if emotion_m else None
        confidence = float(conf_m.group(1)) if conf_m else None

        if emotion not in EMOTIONS:
            raise ValueError(f"Unexpected emotion: {emotion!r}")

        return {
            "emotion": emotion,
            "confidence": round(confidence, 2) if confidence is not None else None
        }

    except Exception as e:
        print(f"Error detecting emotion: {e}")
        return {"emotion": None, "confidence": None}
    




def calculate_compliance_score(conversation):
    client = OpenAI(api_key=config.get('OPENAI_API_KEY'))

    formatted_chat = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in conversation])

    prompt = (
        "You are a compliance auditor evaluating customer support conversations.\n"
        "Here are the compliance rules:\n" +
        "\n".join([f"{i+1}. {rule}" for i, rule in enumerate(COMPLIANCE_RULES)]) + "\n\n"
        "Conversation:\n" + formatted_chat + "\n\n"
        "Evaluate whether each compliance rule was followed. "
        "Respond exactly in the format:\n"
        "Rule 1: ✅ or ❌\n"
        "Rule 2: ✅ or ❌\n"
        "Rule 3: ✅ or ❌\n"
        "Rule 4: ✅ or ❌\n"
        "Rule 5: ✅ or ❌\n"
        "Compliance Score: <percentage>%"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert compliance checker for support conversations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )

        content = response.choices[0].message.content.strip()
        print("Model Response:\n", content)

        checks = re.findall(r'Rule \d:\s*(✅|❌)', content)
        followed = sum(1 for c in checks if c == '✅')
        total = len(COMPLIANCE_RULES)

        # Fallback if compliance score is directly mentioned
        score_match = re.search(r'Compliance Score:\s*(\d+)', content)
        if score_match:
            compliance_score = int(score_match.group(1))
        else:
            compliance_score = round((followed / total) * 100)

        return {
            "score": compliance_score,
            "rules_followed": followed,
            "total_rules": total,
            "raw_output": content
        }

    except Exception as e:
        print(f"Error during compliance evaluation: {e}")
        return {
            "score": 0,
            "rules_followed": 0,
            "total_rules": len(COMPLIANCE_RULES),
            "raw_output": None
        }
