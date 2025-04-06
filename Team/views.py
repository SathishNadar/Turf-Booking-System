from django.shortcuts import render, redirect
from django.http import HttpResponse
from Admin.models import Registration
from Organizer.models import Turfregistration,Host_Tournament
from .models import Tournament_Booking,Turf_Booking,rating
from hashlib import sha256
from django.views.decorators.cache import cache_control
from django.db.models import Q
from django.contrib import messages
import datetime
import paypalrestsdk
from django.conf import settings

# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def tournament_booking(request,id):
    Tournament_details=Host_Tournament.objects.get(id=id)
    m=Tournament_details.uid
    user_id = request.session['id']
    dis = Registration.objects.get(id=user_id)
    reg=Turfregistration.objects.get(uid=m)
    if request.method=='POST':
        ob=Tournament_Booking()
        ob.uid=user_id
        ob.user_name=dis
        ob.tid=Tournament_details.id
        ob.Tournament_name=Tournament_details
        ob.turf_id=reg.id
        if (Tournament_Booking.objects.filter(uid=dis.id,tid=Tournament_details.id)).exists():
            return HttpResponse('Already Booked For This Tournament')
        else:
            ob.save()
            return HttpResponse('Tournament Booked')
    else:
        return HttpResponse('Something went wrong!...')

def turf_booking_details(request,id):
    turf_details=Turfregistration.objects.get(id=id)
    if 'id' in request.session:
        user_id = request.session['id']
        dis = Registration.objects.get(id=user_id)
        time_slot = Turf_Booking.objects.filter()
        return render(request,'turf_book.html', {'id': user_id,'dis':dis,'turf_details':turf_details,'time_slot':time_slot})
    else:
        return HttpResponse('You need to login to Book!')



# PayPal SDK configuration
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" for testing, "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def turf_booking(request, id):
    turf_details = Turfregistration.objects.get(id=id)
    turfid = turf_details.id
    if 'id' in request.session:
        user_id = request.session['id']
        dis = Registration.objects.get(id=user_id)
        if request.method == 'POST':
            ob = Turf_Booking()
            st = request.POST.get('start_time')
            et = request.POST.get('end_time')
            dt = request.POST.get('turf_date')
            today = datetime.datetime.now().strftime('%Y-%m-%d')

            # Validation
            if st == '' or et == '' or dt == '':
                return HttpResponse('All Fields need to be Filled!')
            elif dt < today:
                return HttpResponse('Select another date')

            # Check if the time slot is already booked
            if Turf_Booking.objects.filter(date=dt, start_time=st, end_time=et, turf_id=turfid).exists():
                return HttpResponse('Time is not available')

            # Save booking
            ob.uid = user_id
            ob.user_name = dis
            ob.Turf_name = turf_details
            ob.turf_id = turf_details.id
            ob.date = dt
            ob.start_time = st
            ob.end_time = et
            ob.is_available = 1
            ob.save()

            # Redirect to PayPal for payment
            rate = turf_details.turf_rate  # Use the rate set by the organizer
            return redirect('create_paypal_payment', booking_id=ob.id, amount=rate)
    else:
        return HttpResponse('You need to log in to book a turf.')


def rate(request,id):
    turf_details = Turfregistration.objects.get(id=id)
    turfid=turf_details.id
    if 'id' in request.session:
        user_id = request.session['id']
        dis = Registration.objects.get(id=user_id)
        if request.method == 'POST':
            ob=rating()
            star = request.POST.get('rate')
            ob.uid=user_id
            ob.user_name=dis
            ob.Turf_name=turf_details.turf_name
            ob.turf_id=turf_details.id
            ob.star=star
            if(rating.objects.filter(uid=user_id,turf_id=turf_details.id)).exists():
                rating.objects.filter(uid=user_id,turf_id=turf_details.id).update(star=star)
                return HttpResponse('Rating updated')
            ob.save()
            return HttpResponse('Rating given')
        return redirect('about')
    
def create_paypal_payment(request, booking_id, amount):
     try:
          booking = Turf_Booking.objects.get(id=booking_id)
          payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/payment-success/'),
            "cancel_url": request.build_absolute_uri('/payment-cancelled/')
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": booking.Turf_name,
                    "sku": "Turf Booking",
                    "price": str(amount),  # The rate of the turf
                    "currency": "EUR",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(amount),
                "currency": "EUR"
            },
            "description": f"Turf booking for {booking.Turf_name}"
        }]
    })
          if payment.create():
              for link in payment.links:
                  if link.rel == "approval_url":
                     return redirect(link.href)  # Redirect to PayPal approval page
          else:
           error_message = payment.error
           print(f"PayPal Payment Error: {error_message}")
           return HttpResponse('Error occurred during PayPal payment creation.{error_message}')
     except Exception as e:
    # Catch any exception that may occur and display an error message
    
       return HttpResponse(f'An error occurred: {str(e)}')

def payment_success(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    # Find the payment
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return HttpResponse('Payment successful! Your booking is confirmed.')
    else:
        return HttpResponse('Payment failed.')

def payment_cancelled(request):
    return HttpResponse('Payment was cancelled by the user.')

         
    

               
        
       
   

