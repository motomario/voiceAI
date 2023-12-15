import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from openai import OpenAI

client = OpenAI(api_key="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")

def index(request):
    return render(request, 'voiceAI/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def process_command(request):
    transcript = request.POST.get('transcript', '')

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
                                                  messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                            {"role": "user", "content": transcript}])
        response = json.loads(response.model_dump_json())
        ai_response = response['choices'][0]['message']['content']

        response_data = {'message': ai_response}
    except Exception as e:
        response_data = {'error': str(e)}

    return JsonResponse(response_data)
