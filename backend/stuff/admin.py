from django.contrib import admin
from .models import (
    Location,
    DetectorModel,
    DetectorModelConfiguration,
    Detector,
    LocationDetectorSlot,
    LocationDetectorLog,
    DetectorFault,
    Maintenance,
    MaintenanceTask,
    CylinderType,
    CylinderModel,
    Cylinder,
    CylinderFault,
    SensorType,
    Sensor,
    SensorSlot,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "location_type", "priority", "district")
    list_filter = ("location_type", "district")
    search_fields = ("label", "address", "district")
    ordering = ("-priority", "location_type", "label")


@admin.register(DetectorModel)
class DetectorModelAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "manufacturer", "detector_type", "supplier", "part_number")
    list_filter = ("manufacturer", "detector_type", "supplier")
    search_fields = ("label", "part_number")


@admin.register(DetectorModelConfiguration)
class DetectorModelConfigurationAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "detector_model")
    search_fields = ("label", "detector_model__label")
    raw_id_fields = ("detector_model",)


@admin.register(Detector)
class DetectorAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "serial", "status", "detector_model", "location", "configuration", "created_at", "updated_at")
    list_filter = ("status", "detector_model", "location")
    search_fields = ("label", "serial", "detector_model__label", "location__label")
    raw_id_fields = ("location", "detector_model", "configuration")
    readonly_fields = ("created_at", "updated_at")


@admin.register(LocationDetectorSlot)
class LocationDetectorSlotAdmin(admin.ModelAdmin):
    list_display = ("id", "location", "detector_model")
    search_fields = ("location__label", "detector_model__label")
    autocomplete_fields = ("location", "detector_model")


@admin.register(LocationDetectorLog)
class LocationDetectorLogAdmin(admin.ModelAdmin):
    list_display = ("id", "detector", "old_location", "new_location", "updated")
    list_filter = ("new_location", "old_location", "updated")
    search_fields = ("detector__label", "detector__serial", "new_location__label", "old_location__label")
    raw_id_fields = ("detector", "new_location", "old_location")
    readonly_fields = ("detector", "new_location", "old_location", "updated")
    ordering = ("-updated",)


@admin.register(DetectorFault)
class DetectorFaultAdmin(admin.ModelAdmin):
    list_display = ("id", "detector", "fault_type", "status", "report_dt", "report_location")
    list_filter = ("status", "fault_type")
    search_fields = ("detector__label", "detector__serial", "report_location__label")
    raw_id_fields = ("detector", "report_location")


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("id", "maintenance_type", "status", "detector", "date_due", "date_performed")
    list_filter = ("maintenance_type", "status")
    search_fields = ("detector__label", "detector__serial")
    raw_id_fields = ("detector",)


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "maintenance", "task_type")
    list_filter = ("task_type",)
    search_fields = ("maintenance__detector__label", "maintenance__detector__serial")
    raw_id_fields = ("maintenance",)


@admin.register(CylinderType)
class CylinderTypeAdmin(admin.ModelAdmin):
    # Removed part_number, supplier, and volume as they are now on CylinderModel
    list_display = ("id", "balance_gas", "cylinder_1_gas", "cylinder_1_conc", "cylinder_1_units", "active")
    list_filter = ("active", "balance_gas", "cylinder_1_gas")
    # Removed search_fields for part_number

@admin.register(CylinderModel)
class CylinderModelAdmin(admin.ModelAdmin):
    list_display = ("id", "part_number", "supplier", "volume", "cylinder_type", "percent_error", "expiry_months")
    list_filter = ("supplier", "volume", "cylinder_type")
    search_fields = ("part_number",)
    raw_id_fields = ("cylinder_type",)

@admin.register(Cylinder)
class CylinderAdmin(admin.ModelAdmin):
    # Changed cylinder_type to cylinder_model
    list_display = ("label", "serial", "cylinder_model", "location", "detector", "status", "expiry_date")
    list_filter = ("status", "cylinder_model", "location")
    search_fields = ("cylinder_number", "serial", "location__label", "detector__label")
    raw_id_fields = ("cylinder_model", "location", "detector") # Changed cylinder_type to cylinder_model


@admin.register(CylinderFault)
class CylinderFaultAdmin(admin.ModelAdmin):
    list_display = ("id", "cylinder", "fault_type", "status", "report_dt", "report_location")
    list_filter = ("status", "fault_type")
    search_fields = ("cylinder__cylinder_number", "cylinder__serial", "report_location__label")
    raw_id_fields = ("cylinder", "report_location")


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "part_number", "manufacturer", "sensorgas", "active")
    list_filter = ("active", "manufacturer", "sensorgas")
    search_fields = ("part_number",)


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "serial", "sensor_type", "detector", "status", "expiry_date")
    list_filter = ("status", "sensor_type")
    search_fields = ("serial", "sensor_type__part_number", "detector__label")
    raw_id_fields = ("sensor_type", "detector")


@admin.register(SensorSlot)
class SensorSlotAdmin(admin.ModelAdmin):
    list_display = ("id", "detector", "sensorgas", "sensor")
    list_filter = ("sensorgas",)
    search_fields = ("detector__label", "sensor__serial")
    raw_id_fields = ("detector", "sensor")
