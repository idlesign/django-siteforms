from django.urls import path

from .views import index, themed


urlpatterns = [
    path('', index, name='index'),
    path('<slug:theme>/', themed, name='themed'),
]
