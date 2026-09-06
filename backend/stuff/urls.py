from django.urls import include, path
from rest_framework import routers
from .views import (
    CylinderFaultViewSet, CylinderGasView, CylinderStatusView, CylinderTypeViewSet,
    CylinderUnitView, CylinderViewSet, CylinderVolumeView, DetectorFaultTypeView,
    DetectorFaultViewSet, DetectorModelConfigurationViewSet, DetectorModelViewSet,
    DetectorStatusView, DetectorTypeView, DetectorViewSet, DistrictView,
    LocationDetectorSlotViewSet, LocationDetectorLogViewSet, LocationTypeView,
    LocationViewSet, MaintenanceStatusView, MaintenanceTaskTypeView,
    MaintenanceTaskViewSet, MaintenanceTypeView, MaintenanceViewSet, ManufacturerView,
    SensorGasView, SensorSlotViewSet, SensorStatusView, SensorTypeViewSet,
    SensorViewSet, SupplierView, cylinders_pdf, detector_detail_pdf, detectors_pdf,
    faults_pdf, maintenance_pdf, sensors_pdf, DetectorLabelOnlyViewSet,
    DetectorLocationStatusUpdateView,
)
from .views_auth import (
    CsrfTokenView,
    CurrentUserView,
    LoginView,
    LogoutView,
    PinLoginView,  # <--- Imported
)

router = routers.SimpleRouter()
router.register(r"locations", LocationViewSet)
router.register(r"detectormodels", DetectorModelViewSet)
router.register(r"detectors", DetectorViewSet)
router.register(r"maintenances", MaintenanceViewSet)
router.register(r"maintenancetasks", MaintenanceTaskViewSet)
router.register(r"detectorfaults", DetectorFaultViewSet)
router.register(r"cylindertypes", CylinderTypeViewSet)
router.register(r"cylinders", CylinderViewSet)
router.register(r"cylinderfaults", CylinderFaultViewSet)
router.register(r"locationdetectorslots", LocationDetectorSlotViewSet)
router.register(r"locationdetectorlogs", LocationDetectorLogViewSet)
router.register(r"detectormodelconfigurations", DetectorModelConfigurationViewSet)
router.register(r"sensortypes", SensorTypeViewSet)
router.register(r"sensors", SensorViewSet)
router.register(r"sensorslots", SensorSlotViewSet)
router.register(r"detector-labels", DetectorLabelOnlyViewSet, basename="detector-labels")

urlpatterns = [
    path("detectors/update-location-status/", DetectorLocationStatusUpdateView.as_view(), name="detector-update-location-status"),
    
    path("", include(router.urls)),
    # Choice/list endpoints
    path("location-types/", LocationTypeView.as_view(), name="location-type-list"),
    path("districts/", DistrictView.as_view(), name="district-list"),
    path("manufacturers/", ManufacturerView.as_view(), name="manufacturer-list"),
    path("detector-types/", DetectorTypeView.as_view(), name="detector-type-list"),
    path("suppliers/", SupplierView.as_view(), name="supplier-list"),
    path("detector-statuses/", DetectorStatusView.as_view(), name="detector-status-list"),
    path("maintenance-types/", MaintenanceTypeView.as_view(), name="maintenance-type-list"),
    path("maintenance-task-types/", MaintenanceTaskTypeView.as_view(), name="maintenance-task-type-list"),
    path("maintenance-statuses/", MaintenanceStatusView.as_view(), name="maintenance-status-list"),
    path("detector-fault-types/", DetectorFaultTypeView.as_view(), name="detector-fault-type-list"),
    path("cylinder-gas/", CylinderGasView.as_view(), name="cylinder-gas-list"),
    path("cylinder-unit/", CylinderUnitView.as_view(), name="cylinder-unit-list"),
    path("cylinder-volume/", CylinderVolumeView.as_view(), name="cylinder-volume-list"),
    path("cylinder-statuses/", CylinderStatusView.as_view(), name="cylinder-status-list"),
    path("sensor-statuses/", SensorStatusView.as_view(), name="sensor-status-list"),
    path("sensor-gases/", SensorGasView.as_view(), name="sensor-gas-list"),
    
    # Auth endpoints (NO trailing spaces, correct views)
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("auth/pin-login/", PinLoginView.as_view(), name="api-pin-login"), # <--- Fixed
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
    path("auth/current-user/", CurrentUserView.as_view(), name="current-user"),
    path("csrf-token/", CsrfTokenView.as_view(), name="csrf-token"),
    
    # PDF reports
    path("pdf/detectors/", detectors_pdf, name="pdf-detectors"),
    path("pdf/sensors/", sensors_pdf, name="pdf-sensors"),
    path("pdf/cylinders/", cylinders_pdf, name="pdf-cylinders"),
    path("pdf/maintenance/", maintenance_pdf, name="pdf-maintenance"),
    path("pdf/faults/", faults_pdf, name="pdf-faults"),
    path("pdf/detectors/<int:detector_id>/", detector_detail_pdf, name="pdf-detector-detail"),

]
