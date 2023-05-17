from django.shortcuts import render, redirect
from account.forms import RegistrationForm, AccountAuthenticationForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from account.models import Account
from mystranger_app.models import University


def register_view(request, *args, **kwargs):

    user = request.user
    context = {}
    if user.is_authenticated:
        return HttpResponse(f'You are already authenticated as {user.name} with email - {user.email}')

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            email = form.cleaned_data['email'].lower()
            raw_password = form.cleaned_data['password1']
            account = authenticate(email=email, password=raw_password)

            # add the university if not already added than add the user to that university
            name = email.split('@')[-1:][0]
            university = fetch_or_create_uni(name)
            university.add_user(account)

            login(request, account)
            destination = kwargs.get('next')
            if destination:
                return redirect(destination)
            else:
                return redirect('home')
        else:
            context['registration_form'] = form

    else:
        form = RegistrationForm()
        context['registration_form'] = form

    return render(request, 'account/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request, *args, **kwargs):

    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password = request.POST.get('password')
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                destination = kwargs.get('next')
                if destination:
                    return redirect(destination)
                else:
                    return redirect('home')
        else:
            context['login_form'] = form

    return render(request, 'account/login.html', context)


def account_view(request, *args, **kwargs):
    """
    - Logic here is kind of tricky
            is_self (boolean)
                    is_friend (boolean)
                            -1: NO_REQUEST_SENT
                            0: THEM_SENT_TO_YOU
                            1: YOU_SENT_TO_THEM
    """
    context = {}
    user_id = kwargs.get("user_id")
    try:
        account = Account.objects.get(pk=user_id)
    except:
        return HttpResponse("Something went wrong.")
    if account:
        context['id'] = account.id
        context['name'] = account.name
        context['email'] = account.email

        # Define template variables
        is_self = True

        user = request.user
        if user.is_authenticated and user != account:
            is_self = False
        elif not user.is_authenticated:
            is_self = False

        # Set the template variables to the values
        context['is_self'] = is_self

        return render(request, "account/account.html", context)


def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    account = Account.objects.get(pk=user_id)
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone elses profile.")
    context = {}
    if request.POST:
        name = request.POST.get('name')
        account.name = name
        account.save()
        return redirect("account:view", user_id=account.pk)
    else:
        
        initial={
            "id": account.pk,
            "email": account.email,
            "name": account.name,
            }
        
        context['form'] = initial
    
    return render(request, "account/edit_account.html", context)


'''
Some Functions to make our life easier.
'''

def fetch_or_create_uni(name):
    try:
        university = University.objects.get(name=name)
    except University.DoesNotExist:
        university = University(name=name)
        university.save()
    return university