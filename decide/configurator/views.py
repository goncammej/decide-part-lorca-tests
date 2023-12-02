from django.shortcuts import render

def configurator(request):
    return render(request, 'configurator/configurator.html')
