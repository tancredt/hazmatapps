from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("frvadmin/", admin.site.urls),
    path("api/inventory/", include("stuff.urls")),
]
