from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('core.urls')),
    path('ingest/', include('ingest.urls')),  
    path('core/', include('core.urls')),
    path("search/", include("search.urls")),
    path("chat/", include('chat.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    

