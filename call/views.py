from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def main_view(request):
    context = {}
    return render(request, 'main.html', context=context)