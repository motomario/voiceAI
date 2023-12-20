from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import openai
import logging
import time
import json

# Configure the logger
logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key="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")


class MessageContentText:
    def __init__(self, text, type):
        self.text = text
        self.type = type

    def to_dict(self):
        # Add logging to check the data being processed
        logger.debug(f"Converting MessageContentText to dict with text: {self.text} and type: {self.type}")
        return {
            'text': self.text,
            'type': self.type,
        }


# Custom JSON Encoder
class CustomEncoder(DjangoJSONEncoder):
    def default(self, obj):
        # Add logging to check which object type is being processed
        logger.debug(f"CustomEncoder processing object of type: {type(obj).__name__}")
        if isinstance(obj, MessageContentText):
            return obj.to_dict()
        return super().default(obj)


def index(request):
    return render(request, 'voiceAI/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def process_command(request):
    data = json.loads(request.body)
    transcript = data.get('transcript', '')
    session = request.session.get('session', {})

    logger.info(f"Received transcript: {transcript}")

    try:
        if 'thread_id' not in session:
            thread = client.beta.threads.create()
            session['thread_id'] = thread.id
            request.session['session'] = session

        logger.debug(f"Sending to OpenAI: Thread ID - {session['thread_id']}, Transcript - {transcript}")

        message = client.beta.threads.messages.create(
            thread_id=session['thread_id'],
            role="user",
            content=transcript
        )

        run = client.beta.threads.runs.create(
            thread_id=session['thread_id'],
            assistant_id=settings.OPENAI_ASSISTANT_ID
        )

        while run.status != "completed":
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=session['thread_id'],
                run_id=run.id
            )

        messages = client.beta.threads.messages.list(thread_id=session['thread_id'])
        last_message = next(msg for msg in messages.data if msg.role == "assistant")

        logger.debug(f"Type of last_message.content: {type(last_message.content)}")
        logger.debug(f"Structure of last_message.content: {last_message.content}")
        logger.debug(f"Last message full content: {last_message}")

        if isinstance(last_message.content, list) and len(last_message.content) > 0:
            message_content_obj = last_message.content[0]  # First item of the list
            if hasattr(message_content_obj, 'text') and hasattr(message_content_obj.text, 'value'):
                response_text = message_content_obj.text.value
                response_data = {'message': response_text}
            else:
                raise ValueError("Invalid message content structure")
        else:
            raise ValueError("Invalid message format")

    except Exception as e:
        logger.exception("Error processing the command")
        response_data = {'error': str(e)}

    return JsonResponse(response_data)