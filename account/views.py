from django.shortcuts import render, redirect
from account.forms import RegistrationForm, AccountAuthenticationForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from account.models import Account
from mystranger_app.models import University , UniversityProfile
from django.db.models import Q
from mystranger_app.utils import calculate_distance


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
            lat = request.POST.get('lat')
            lon = request.POST.get('lon')

            # we are creating or fetching the university model but if the info came from user input then we are going to create a university profile, the university model is only going to be created when either it came from the database or it is manually verified from the backend.

            notrust = request.POST.get('notrust')
            if notrust:
                # This means that location is obtained from the user input and can't be trusted therefore we are gonna create a university profile
                uniName = request.POST.get('universityName')
                university_profile = fetch_or_create_uniprofile(name,lat,lon,uniName)
                university_profile.add_user(account)
            else:
                university = fetch_or_create_uni(name,lat,lon)
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

def fetch_or_create_uni(name,Lat,Lon):
    try:
        university = University.objects.get(name=name)
    except University.DoesNotExist:
        university = University(name=name,lat=Lat,lon=Lon)
        university.save()
        
        '''
        This is a very important part of registration, here when we are creating a new university instance for the first time therefore we are also going to calculate all the universities that exist in the 60 km range of this university and add them into the nearby list -

        but the catch here is that - 

        we are all going to add this university to all the NL of universities that lies in the NL of this university
        '''
        nearby_list = []
        universities = University.objects.all()
        for uni in universities:
            Lat1 = uni.lat
            Lon1 = uni.lon

            distance = calculate_distance(Lat,Lon,Lat1,Lon1)
            if distance <= 60:
                '''
                This means that yes this uni lies with in 60 km of registration uni
                '''
                nearby_list.append(uni)
        
        university.nearbyList.add(*nearby_list)
        university.save()

        for uni in nearby_list:
            uni.nearbyList.add(university)
            uni.save()
            
    return university


def fetch_or_create_uniprofile(name,Lat,Lon,uniName):
    try:
        university = UniversityProfile.objects.get(Q(name=name) & Q(lat=Lat) & Q(lon=Lon))
    except UniversityProfile.DoesNotExist:
        university = UniversityProfile(name=name,lat=Lat,lon=Lon,universityName=uniName)
        university.save()
        nearby_list = []
        universities = University.objects.all()
        for uni in universities:
            Lat1 = uni.lat
            Lon1 = uni.lon

            distance = calculate_distance(Lat,Lon,Lat1,Lon1)
            if distance <= 60:
                '''
                This means that yes this uni lies with in 60 km of registration uni
                '''
                nearby_list.append(uni)
        
        university.nearbyList.add(*nearby_list)
        university.save()
    return university