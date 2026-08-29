from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('challan/', include('challan.urls')),
    path('', include('dashboard.urls')),
    # detection / anpr / challan / signal_control apps get wired in here
    # as their views are built (Weeks 3-5 of the roadmap).
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
