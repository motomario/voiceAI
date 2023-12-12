from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import openai

# Make sure to set your OpenAI API key in your environment variables
# or manage it securely in your Django settings
openai.api_key = "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"

def index(request):
    return render(request, 'voiceAI/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def process_command(request):
    transcript = request.POST.get('transcript', '')

    try:
        # Update this part to use the new API interface
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated model name for new API
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": transcript},
            ]
        )

        # Extracting the OpenAI response text
        ai_response = response['choices'][0]['message']['content']  # Adjusted for new response structure

        # Sending the AI response back to the frontend
        response_data = {'message': ai_response}

    except Exception as e:  # Updated to catch a general exception
        # Handle errors more specifically if needed
        response_data = {'error': str(e)}

    return JsonResponse(response_data)
