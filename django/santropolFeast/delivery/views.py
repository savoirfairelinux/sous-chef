from django.views import generic
from django.shortcuts import render

def show_distance(request):
    return render(request, 'map.html')



#def show_distance(request):
#    return HttpResponse('Hello distance')
