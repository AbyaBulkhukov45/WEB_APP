from django.urls import path
from django.views.generic import TemplateView
from django.views.defaults import (
    bad_request, permission_denied, page_not_found, server_error
)
from django.conf.urls.static import static
from django.conf import settings

app_name = 'pages'

urlpatterns = [
    path('about/',
         TemplateView.as_view(template_name='pages/about.html'),
         name='about'),
    path('rules/',
         TemplateView.as_view(template_name='pages/rules.html'),
         name='rules'),
    path('403/', permission_denied, {'exception': Exception('403 Forbidden')}, name='403'),
    path('404/', page_not_found, {'exception': Exception('404 Not Found')}, name='404'),
    path('500/', server_error, name='500'),
]
