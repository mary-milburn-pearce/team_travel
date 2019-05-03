
from django.shortcuts import render, redirect, HttpResponse
# from google.oauth2 import service_account
import datetime, random, re, datetime, bcrypt
from django.contrib import messages
from apps.login.models import Person
from urllib.parse import urlparse

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

def user_login(session, user_id, fname, lname, email):
    session['user_id']=user_id
    session['first_name']=fname
    session['last_name']=lname
    session['email']=email
    session['logged-in']=True
    print(f"User: {user_id}, {fname} {lname} LOGGED IN")

def user_registered(email_addr):
    try:
        user = Person.objects.get(email=email_addr)
    except:
        return False
    else:
        return user
    
def save_post_data(postData):
    context = { 'fname' : postData['fname'],
                'lname' : postData['lname'],
                'email' : postData['email'] }
    return context

def index(request):
    request.session['logged-in']=False
    return render(request, "login/index.html")

def register(request):
    request.session['logged-in']=False
    errors = Person.objects.basic_validation(request.POST)
    is_valid = True
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        is_valid = False
    else:
        if user_registered(request.POST['email']):
            messages.error(request, "This email address is already registered")
            is_valid=False
        else:
            hashed_pw = bcrypt.hashpw(request.POST['pw'].encode(), bcrypt.gensalt())
            user = Person.objects.create( \
                    first_name=request.POST['fname'], \
                    last_name=request.POST['lname'], \
                    email=request.POST['email'], \
                    password=hashed_pw)
            if not user:
                messages.error(request, "User could not be added")
                is_valid=False
    if is_valid:
        user_login(request.session, user.id, user.first_name, user.last_name, user.email)
        return redirect(f"/dashboard/{user.id}")
    else:
        context = save_post_data(request.POST)
        return render(request, "login/index.html", context)

def login(request):
    is_valid=True
    request.session['logged-in']=False
    if not EMAIL_REGEX.match(request.POST['email']): 
        messages.error(request, "Invalid email address!")
        is_valid=False
    if len(request.POST['pw'])<1:
        messages.error(request, "Please enter password")
        is_valid=False
    if is_valid:
        user=user_registered(request.POST['email'])
        if not user:
            messages.error(request, "User not yet registered")
            is_valid=False
        else:
            hashed_pw = bcrypt.hashpw(request.POST['pw'].encode(), bcrypt.gensalt())
            if not bcrypt.checkpw(request.POST['pw'].encode(), user.password.encode()):
                messages.error(request, "Invalid login")
                is_valid=False
    if is_valid:
        user_login(request.session, user.id, user.first_name, user.last_name, user.email)
        return redirect(f"/dashboard/{user.id}")
    else:
        return render(request, "login/index.html")

def logout(request):
    print(f"User: {request.session['user_id']}, {request.session['first_name']} {request.session['last_name']} LOGGED OUT")
    request.session.clear()
    request.session['logged-in']=False
    return redirect("/")

def login_google(request):
    # request.session['logged-in']=False
    # print ("In google login!")
    # # Login with service account - WORKING
    # # SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin',
    # #     'https://www.googleapis.com/auth/drive.file',  #Drive v3
    # #     'https://www.googleapis.com/auth/drive.metadata',   #Drive v3
    # #     'https://www.googleapis.com/auth/userinfo.email',  #OAuth2 v2
    # #     'https://www.googleapis.com/auth/userinfo.profile',  #OAuth2 v2
    # #     'https://www.googleapis.com/auth/spreadsheets']   #Sheets v4
    # # SERVICE_ACCOUNT_FILE = './team-travel-238415-5d651ecfa747.json'
    # # credentials = service_account.Credentials.from_service_account_file(
    # #     SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # # if credentials:
    # #     print(credentials)
    # #     return redirect(f"/dashboard/{user.id}")
    # # else:
    # #     return redirect("/")

    # # Login with User Flow - WORKING
    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    #     'client_secret.json',
    #     scopes=['email', 'profile',
    #         'https://www.googleapis.com/auth/drive.file'])

    # flow.redirect_uri = 'http://localhost:8000/signincallback'

    # # Generate URL for request to Google's OAuth 2.0 server.
    # authorization_url, state = flow.authorization_url(
    #     # Enable offline access so that you can refresh an access token without
    #     # re-prompting the user for permission. Recommended for web server apps.
    #     access_type='offline',
    #     # Enable incremental authorization. Recommended as a best practice.
    #     include_granted_scopes='true')
    # print("Authorization URL:", authorization_url)
    # request.session['flow']=flow
    return redirect(authorization_url)

    # return render(request, "login/google_auth.html")

def signin_callback(request):
    print(request)
    # http://example.com/auth_return/?code=kACAH-1Ng1MImB...AA7acjdY9pTD9M
    # http://example.com/auth_return/?error=access_denied
    flow=request.session['flow']
    # o=urlparse()
    # credentials = flow.step2_exchange(code)
    return redirect("/")
