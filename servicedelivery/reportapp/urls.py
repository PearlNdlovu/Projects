from django.urls import path
from . import views

urlpatterns = [
    path('lodge/', views.lodge_complaint, name='lodge_complaint'),
    path('success/<str:ref>/', views.complaint_success, name='complaint_success'),
    path('track/', views.track_complaint, name='track_complaint'),
    path('rate/', views.submit_rating, name='submit_rating'),
    path('api/chat/', views.report_chat_api, name='report_chat_api'),
]
