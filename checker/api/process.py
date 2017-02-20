from django.http import JsonResponse
from checker.tasks import base
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'result': base.get()
            })
        else:
            raise Exception('Method not GET')
    except BaseException as e:
        return JsonResponse({
            'success': False,
            'result': str(e)
        })
    