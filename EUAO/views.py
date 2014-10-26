# Create your views here.
from EUAO.euao_function import *

def reset_euao_data(request):
    test_delete_euao_check_task()
    test_delete_euao_task()
    return HttpResponse("Rest all euao complete!")
