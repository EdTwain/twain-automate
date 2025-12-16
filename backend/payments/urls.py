from django.urls import path
from .import views
urlpatterns=[
    path('',views.home,name='home'),
    path('pay/',views.lipa_na_mpesa,name='pay'),
    path('callback/',views.callback,name='callback'),
]
