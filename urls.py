from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.form_view, name='form'),
    path('submit/', views.submit_form, name='submit_form'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
