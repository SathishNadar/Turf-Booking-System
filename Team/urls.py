from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    path('tournament_booking/<id>',tournament_booking,name='tournament_booking'),
    path('turf_booking_details/<id>',turf_booking_details,name='turf_booking_details'),
    path('turf_booking/<id>',turf_booking,name='turf_booking'),
    path('rate/<id>',rate,name='rate'),
     path('turf_booking/<int:id>/', views.turf_booking, name='turf_booking'),
    path('create-paypal-payment/<int:booking_id>/<str:amount>/', views.create_paypal_payment, name='create_paypal_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
