from django.http import HttpResponse,Http404
import datetime

from vmware_function import *

def rest_all(request):
    test_reset_all()
    return HttpResponse("Rest all vmwrare data complete!")
