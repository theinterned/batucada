from django.conf.urls.defaults import *

from dashboard import views

urlpatterns = patterns('',
    (r'^dashboard/', views.dashboard),
)
