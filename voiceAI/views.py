import json
import openai
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

# Configure the logger
logger = logging.getLogger(__name__)

# Instantiate the OpenAI client with your API key
client = openai.OpenAI(api_key="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")

def index(request):
    return render(request, 'voiceAI/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def process_command(request):
    # Retrieve the transcript from the POST data
    transcript = request.POST.get('transcript', '')

    # Retrieve the conversation history from the session
    conversation_history = request.session.get('conversation_history', [])

    logger.debug(f"Received transcript: {transcript}")
    logger.debug(f"Current conversation history: {conversation_history}")

    try:
        # Add the user's message to the conversation history
        conversation_history.append({"role": "user", "content": transcript})

        # Log the updated conversation history
        logger.debug(f"Updated conversation history: {conversation_history}")

        # Since this is a chat model, use the chat completion endpoint
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )

        # Parse the API response
        ai_response = response.choices[0].message.content

        # Add the AI's response to the conversation history
        conversation_history.append({"role": "assistant", "content": ai_response})

        # Save the updated conversation history back to the session
        request.session['conversation_history'] = conversation_history

        # Prepare the response data
        response_data = {'message': ai_response}
    except Exception as e:
        # Log the error
        logger.exception("Error processing the command")
        # Handle exceptions and prepare the error response
        response_data = {'error': str(e)}

    # Return the AI's response as a JSON
    return JsonResponse(response_data)
