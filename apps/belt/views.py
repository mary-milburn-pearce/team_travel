from django.shortcuts import render, redirect, HttpResponse
from apps.login.models import Person
from .models import Event, EventRequest, EarthPoints
from django.contrib import messages
import datetime, json
from django import forms
from django.core.files.storage import FileSystemStorage
	
def show_dashboard(request, person_id):
    if not request.session['logged-in']:
        return redirect("/")
    p = Person.objects.get(id=person_id)
    h_events = Event.objects.filter(organizer=p)
    a_events = p.attending_events.all()
    o_events = Event.objects.exclude(organizer=p)
    for a in a_events:
        o_events = o_events.exclude(id=a.id)
    reqs = p.requested_trips.all()
    r_events = []
    for r in reqs.all():
        r_events.append(r.trip)
        o_events = o_events.exclude(id=r.trip.id)
    context = { 'this_person' : p,
                'h_events' : h_events,
                'a_events' : a_events,
                'o_events' : o_events,
                'r_events' : r_events }
    return render(request, "belt/dashboard.html", context)

def show_new_event_form(request):
    if request.session['logged-in']:
        return render(request, "belt/add_event.html")
    else:
        return redirect("/")

def add_event(request):
    if not request.session['logged-in']:
        return redirect("/")
    errors = Event.objects.basic_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        context = { 'dest': request.POST['dest'],
                    'start_dt' : request.POST['start_dt'],
                    'end_dt' : request.POST['end_dt'],
                    'plan' : request.POST['plan']
        }
        return render(request, "belt/add_event.html", context)
    host=Person.objects.get(id=request.session['user_id'])
    ev=Event.objects.create(destination=request.POST['dest'],
                start_date=request.POST['start_dt'],
                end_date=request.POST['end_dt'],
                by_request=request.POST['part_type'],
                plan=request.POST['plan'],
                organizer=host)
    #req_rel_date = datetime.datetime.strptime(request.POST['ev_date'], '%Y-%m-%d')
    if not ev:
        messages.error(request, "Could not add this trip")
        return render(request, "belt/add_event.html", context)
    else:
        return redirect(f"/dashboard/{request.session['user_id']}")
    
def edit_event(request, event_id):         
    if not request.session['logged-in']:
        return redirect("/")
    this_ev=Event.objects.get(id=event_id)
    context = { 'id' : this_ev.id,
                'dest' : this_ev.destination,
                'start_dt' : this_ev.start_date.strftime('%Y-%m-%d'), 
                'end_dt' : this_ev.end_date.strftime('%Y-%m-%d'),
                'plan' : this_ev.plan,
                'request' : this_ev.by_request
    }
    return render(request, "belt/edit_event.html", context)

def update_event(request, event_id):       
    if not request.session['logged-in']:
        return redirect("/")
    errors = Event.objects.basic_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        ev=Event()
        ev.destination=request.POST['dest'],
        ev.start_date=request.POST['start_dt'],
        ev.end_date=request.POST['end_dt'],
        ev.plan=request.POST['plan']
        context = { 'this_ev' : ev }
        return render(request, "belt/edit_event.html", context)
    this_ev=Event.objects.get(id=event_id)
    this_ev.destination=request.POST['dest']
    this_ev.start_date=datetime.datetime.strptime(request.POST['start_dt'], '%Y-%m-%d')
    this_ev.end_date=datetime.datetime.strptime(request.POST['end_dt'], '%Y-%m-%d')
    this_ev.plan=request.POST['plan']
    this_ev.save()  
    return redirect(f"/dashboard/{request.session['user_id']}")

def delete_event(request, event_id):       
    if not request.session['logged-in']:
        return redirect("/")
    ev=Event.objects.get(id=event_id)
    success=ev.delete()
    return redirect(f"/dashboard/{request.session['user_id']}")

def show_one_event(request, event_id):
    if not request.session['logged-in']:
        return redirect("/")
    ev=Event.objects.get(id=event_id)
    context = { 'event' : ev,
                'host' : ev.organizer,
                'coming' : ev.attendees.all(),
                'reqs' : ev.requests.all()}
    return render(request, "belt/show_event.html", context)

def add_to_context(joint_trips, h, me, them):
    tot_pts=0
    pts=EarthPoints.objects.filter(trip=h, awarded_by=me, awarded_to=them)
    for pt in pts:
        tot_pts+=pt.points
    joint_trips.append( { 'trip' : h, 'pts' : tot_pts } )
    print(joint_trips)
    return

def view_profile(request, p_id):
    if not request.session['logged-in']:
        return redirect("/")
    them=Person.objects.get(id=p_id)
    me=Person.objects.get(id=request.session['user_id'])
    joint_trips = []
    for h in them.hosted_events.all():
        a=h.attendees.filter(id=me.id)
        if len(a) > 0:
            add_to_context(joint_trips, h, me, them)
    for h in me.hosted_events.all():
        a=h.attendees.filter(id=them.id)
        if len(a) > 0:
            add_to_context(joint_trips, h, me, them)
    for h in me.attending_events.all():
        a=h.attendees.filter(id=them.id)
        if len(a) > 0:
            add_to_context(joint_trips, h, me, them)
    context = { 'profile' : them,
                'tot_points' : calc_earth_points(them.id),
                'our_trips' : joint_trips }
    return render(request, "belt/profile.html", context) 

def edit_profile(request):
    p=Person.objects.get(id=request.session['user_id'])
    context = { 'me' : p,
                'photo' : p.photo }
    return render(request, "belt/edit_profile.html", context) 

def update_profile(request):
    p=Person.objects.get(id=request.session['user_id'])
    p.first_name=request.POST['fname']
    p.last_name=request.POST['lname']
    p.user_name=request.POST['uname']
    p.email=request.POST['email']
    p.description=request.POST['desc']
    p.save()
    return redirect(f"/dashboard/{request.session['user_id']}")


def join_event(request, event_id):
    if not request.session['logged-in']:
        return redirect("/")
    p=Person.objects.get(id=request.session['user_id'])
    ev=Event.objects.get(id=event_id)
    if not ev.by_request:
        ev.attendees.add(p)
    else:
        trip=EventRequest.objects.create(trip=ev, requestor=p)
    return redirect(f"/dashboard/{request.session['user_id']}")

def unjoin_event(request, event_id):
    if not request.session['logged-in']:
        return redirect("/")
    p=Person.objects.get(id=request.session['user_id'])
    ev=Event.objects.get(id=event_id)
    ev.attendees.remove(p)
    return redirect(f"/dashboard/{request.session['user_id']}")

def cancel_request(request, event_id):
    if not request.session['logged-in']:
        return redirect("/")
    p=Person.objects.get(id=request.session['user_id'])
    ev=Event.objects.get(id=event_id)
    reqs=EventRequest.objects.filter(trip=ev, requestor=p)
    for req in reqs:
        req.delete()
    return redirect(f"/dashboard/{request.session['user_id']}")

def decline_request(request, event_id, p_id):
    if not request.session['logged-in']:
        return redirect("/")
    p=Person.objects.get(id=request.session['user_id'])
    ev=Event.objects.get(id=event_id)
    reqs=EventRequest.objects.filter(trip=ev, requestor=p)
    for req in reqs:
        req.delete()
    return redirect(f"event/{event_id}")

def accept_request(request, event_id, p_id):
    if not request.session['logged-in']:
        return redirect("/")
    p=Person.objects.get(id=request.session['user_id'])
    ev=Event.objects.get(id=event_id)
    reqs=EventRequest.objects.filter(trip=ev, requestor=p)
    for req in reqs:
        req.delete()
    ev.attendees.add(p)
    return redirect(f"event/{event_id}")

def calc_earth_points(user_id):
    recs=EarthPoints.objects.filter(awarded_to__id=user_id)
    tot_pts=0
    for rec in recs:
        tot_pts+=rec.points
    return tot_pts

def create_post(request):
    if request.method == 'POST':
        print(request.POST)
        points = int(request.POST['points'])
        ev=Event.objects.get(id=request.POST['trip_id'])
        givee=Person.objects.get(id=request.POST['to_id'])
        giver=Person.objects.get(id=request.POST['from_id'])
        recs=EarthPoints.objects.filter(trip=ev, awarded_by=giver, awarded_to=givee)
        if len(recs) > 0:
            rec=recs[0]
            rec.points=points
            rec.save()
        else:
            rec=EarthPoints.objects.create(trip=ev, awarded_by=giver, awarded_to=givee, points=points)
        return HttpResponse(
            json.dumps({"total_points": calc_earth_points(request.POST['to_id'])}),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def photo_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        print(myfile)
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print(filename)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        p=Person.objects.get(id=request.session['user_id'])
        p.photo=uploaded_file_url
        p.save()
    return redirect("/profile/edit")

def google_response(request):
    print(request)
    return HttpResponse("Made it to Google response form!")
