from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def submit_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            return JsonResponse({'status': 'success', 'data': data})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'invalid JSON'}, status=400)
    return JsonResponse({'error': 'invalid method'}, status=400)
