from django.shortcuts import render

# Create your views here.
def home_view(request):
    return render(request,'home.html')

def new_chat_view(request):
    return render(request,'new_chat.html')\
    
def new_chat_text_view(request):
    return render(request,'new_chat_text.html')
