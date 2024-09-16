"""
URL configuration for health_predict project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('ai_chat/', include('ai_chat.urls', namespace='ai_chat')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('communication/', include('communication.urls', namespace='communication')),
    path('consultation/', include('appiontment.urls')),
    path('doctor/', include('doctor.urls', namespace='doctor')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),

    path('pharmacy/', include('pharmacy.urls')),
    path('select2/', include('django_select2.urls')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('patient/', include('patient.urls', namespace='patient')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
