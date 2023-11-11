from django.shortcuts import render, redirect
from mystranger_app.models import Feedback
from mystranger_app.models import University, UniversityProfile

# Create your views here.
def home_view(request):

    context = {}
    if request.user.is_authenticated:
        user = request.user
        # checking if user's uni exist or the user is using uni prof instead
        uni_name = user.university_name
        try:
            universi = University.objects.get(name=uni_name)
        except University.DoesNotExist:
            try:
                universi_prof = UniversityProfile.objects.get(name=uni_name)
                context['unverified_uni'] = 'True'
                context['prof_email'] = universi_prof.name
                context['prof_name'] = universi_prof.universityName
            except UniversityProfile.DoesNotExist:
                print('something went wrong....')
    return render(request,'home.html', context)

def new_chat_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request,'new_chat.html')
    
def new_chat_text_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request,'new_chat_text.html')

def error_404_view(request, exception):
    return render(request, 'error_404.html')

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
