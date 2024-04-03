from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AreaViewSet, ExportDataViewSet, ImportDataViewSet, StatusViewSet
from rest_framework.routers import SimpleRouter
APPEND_SLASH = False
router = SimpleRouter(trailing_slash=False)

router = SimpleRouter(trailing_slash=False)
router.register(r"areas", AreaViewSet, "areas")

router_status = SimpleRouter(trailing_slash=False)
router_status.register(r"statuses", StatusViewSet, "status")

router_export = SimpleRouter(trailing_slash=False)
router_export.register(r"export-data", ExportDataViewSet, "export-data")

router_import = SimpleRouter(trailing_slash=False)
router_import.register(r"import-data", ImportDataViewSet, "export-data")

app_name = "common"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(router_status.urls)),
    path("", include(router_export.urls)),
    path("", include(router_import.urls)),
]
