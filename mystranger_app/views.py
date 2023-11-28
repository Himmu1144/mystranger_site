from django.shortcuts import render, redirect
from mystranger_app.models import Feedback
from mystranger_app.models import University, UniversityProfile
from django.http import HttpResponse
from account.models import Account , deleted_account
from django.contrib.auth import authenticate
from django.core.mail import send_mail


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
        context['response'] = "We've recieved your message....."
        # context['msg'] = "It may not a big deal for you but for us it is"


    return render(request,'feedback_form.html',context)


def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')

def delete_account_view(request):

    user = request.user
    context = {}
    if not user.is_authenticated:
        return redirect('login')
    
    if request.method=='POST':

        password = request.POST.get('password')
        reason = request.POST.get('txt')

        email = user.email
        account = authenticate(email=email, password=password)
        if account:
            deleted_account_obj = deleted_account(email=email, name=user.name, reason = reason)
            deleted_account_obj.save()
            account.delete()
            send_email_view(request, email)
            # return render(request, 'account_deleted.html')
            return HttpResponse("""
                    <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Account Deleted!</title>
                        </head>
                        <body>
                                <div class="container">

                            <div class="">
                                <div class="h-100 p-5 bg-body-tertiary border rounded-3" style='text-align:center;'>
                                <h2>Your Account Has Been Successfully Deleted!</h2>
                                <p class="" style="font-size:18px; margin-top:0.5em;">You'll recieve an email from <a href="https://mystranger.in/">mystranger.in</a> informing you about your account deletion.</p>
                                </div>
                            </div>

                        </div>
                        </body>
                        </html>
                    """)
        else:
            context['wrong'] = 'The password you have entered is incorrect! '
            return render(request, 'delete_account.html', context)

    return render(request, 'delete_account.html', context)

def aboutus_view(request):
    return HttpResponse('About Us view')

def terms_view(request):
    return render(request, 'terms.html')


def send_email_view(request, email):
    try:

        subject = 'MyStranger | Your account has been deleted!'
        message = f"We are deeply sorry that you don't like mystranger.in | You are alway's welcome to create your account again by visiting https://mystranger.in/register | If you haven't deleted your account on mystranger.in and still getting this mail than either reply back or send a mail to info@mystranger.in."
        # message = f'Hi paste the link to verify your account http://127.0.0.1:8000/account/verify/{token}'
        from_email = 'info@mystranger.in'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        
    except Exception as e:
        print(e)
