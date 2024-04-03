from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include

schema_view = get_schema_view(
    openapi.Info(
        title="API Documents",
        default_version="v1",
    ),
    public=True,
)

schema_api_docs = []

if settings.DEBUG:
    schema_api_docs = [
        path(
            "",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="Schema Swagger UI",
        ),
    ]

# version_reg = "(?P<version>[v1,v2]+)"

urlpatterns = (
    [
        path("api/admin/", admin.site.urls),
        re_path(f"api/common/", include("common.urls")),
    ]
    + staticfiles_urlpatterns()
    + schema_api_docs
)
