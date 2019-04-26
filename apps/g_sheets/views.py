import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from django.shortcuts import render, redirect, HttpResponse
from apps.login.models import Person

def auth_g_sheets(request):
        # if not creds or not creds.valid:
        # if creds and creds.expired and creds.refresh_token:
        #     creds.refresh(Request())
        # else:
        #     flow = InstalledAppFlow.from_client_secrets_file(
        #         'credentials.json', SCOPES)
        #     creds = flow.run_local_server()
        # # Save the credentials for the next run
        # with open('token.pickle', 'wb') as token:
        #     pickle.dump(creds, token)
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive.file'])

    flow.redirect_uri = 'http://localhost:8000/oauth2callback'

    # Generate URL for request to Google's OAuth 2.0 server.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    print("Authorization URL:", authorization_url)
    return redirect(authorization_url)

def oauth2_landing(request):
    return HttpResponse("Made it to Landing!!!!!")

def open_g_sheet(request):
    SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    SAMPLE_RANGE_NAME = 'Class Data!A2:E'
    #service = build('api_name', 'api_version', ...)
    # The method returns an apiclient.http.HttpRequest object that encapsulates
    # all information needed to make the request, but it does not call the API.
    #request = service.volumes().list(source='public', q='android')
    # The execute() function on the HttpRequest object actually calls the API.
    #response = request.execute()
    # Call the Sheets API
    #service = build('books', 'v1', credentials=creds)
    service = build('sheets', 'v4', developerKey='AIzaSyBLyNdrGJHSWcQWvOJEhEMgd18xshwbo5Q')

    # Call the Sheets API
    sheet = service.spreadsheets() 
    #result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                            range=SAMPLE_RANGE_NAME).execute()
    spreadsheet_body = {
        # TODO: Add desired entries to the request body.
    }
    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()
    #result=sheet.create(body=*, x__xgafv=None)
    return HttpResponse("Made it - created spreadsheet!!!")