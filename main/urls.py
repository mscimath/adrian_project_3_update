from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('services_list/', views.services_list, name='services_list'),
    path('', views.index, name='index'),
    path('services/', views.services, name='services'),

    path(
        "manage_reservation/<int:pk>/",
        views.manage_reservation,
        name="manage_reservation"
    ),

    path('login/', views.user_login, name='login'),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='index'),
        name='logout'
    ),

    path('calendar/', views.calendar_view, name='calendar'),
    path('reservation/', views.reservation, name='reservation'),
    path('chatbot/', views.chat_bot_page, name='chatbot'),
    path('reviews/', views.reviews_page, name='reviews_page'),
    path('reviews/manage/', views.review_manage, name="review_manage"),
    path('reviews/delete/<int:pk>/', views.delete_review, name="delete_review"),
    path('blog/', views.blog, name='blog'),
    path('career/', views.career, name='career'),
    path('contact/', views.contact, name='contact'),

    ]
