from django.shortcuts import render, redirect
from mystranger_app.models import Feedback

# Create your views here.
def home_view(request):
    return render(request,'home.html')

def new_chat_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request,'new_chat.html')
    
def new_chat_text_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request,'new_chat_text.html')

def feedback_view(request):

    if not request.user.is_authenticated:
        return redirect("login")
    
    context = {}
    if request.method == 'POST':

        message = request.POST.get('message')
        user = request.user
        feedback = Feedback(user = user, message = message)
        feedback.save()
        context['response'] = "We Truely Appreciate Your Feedback"
        # context['msg'] = "It may not a big deal for you but for us it is"


    return render(request,'feedback_form.html',context)
