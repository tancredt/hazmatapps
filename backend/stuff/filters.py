from django_filters import rest_framework as filters
from django.db import models
from django.db.models import Q

from .models import (
    District,
    Location,
    DetectorModel,
    Detector,
    DetectorModelConfiguration,
    LocationDetectorSlot,
    LocationDetectorLog,
    DetectorFault,
    Maintenance,
    MaintenanceTask,
    CylinderType,
    Cylinder,
    CylinderFault,
    SensorType,
    Sensor,
    SensorSlot
)

class LocationFilter(filters.FilterSet):
    label = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    district = filters.CharFilter(lookup_expr='iexact')
    district_icontains = filters.CharFilter(
        field_name='district',
        lookup_expr='icontains'
    )
    location_type = filters.CharFilter(lookup_expr='iexact')
    location_type_exclude = filters.CharFilter(field_name='location_type', lookup_expr='exact', exclude=True)
    
    detector_model = filters.NumberFilter(method='filter_detector_model')

    def filter_detector_model(self, queryset, name, value):
        # Filter locations that have at least one LocationDetectorSlot for the given detector_model
        return queryset.filter(detector_model_slots__detector_model=value).distinct()

    class Meta:
        model = Location
        fields = [
            'label',
            'address',
            'district',
            'district_icontains',
            'location_type',
            'location_type_exclude',
            'detector_model' 
        ]

class DetectorModelFilter(filters.FilterSet):
    detector_type = filters.CharFilter(lookup_expr='iexact')
    label = filters.CharFilter(lookup_expr='icontains')
    
    label_exact = filters.CharFilter(field_name='label', lookup_expr='iexact')

    class Meta:
        model = DetectorModel
        fields = ['detector_type', 'label', 'label_exact']

class DetectorFilter(filters.FilterSet):
    label = filters.CharFilter(lookup_expr='icontains')
    serial = filters.CharFilter(lookup_expr='icontains')
    status = filters.CharFilter(lookup_expr='iexact')
    configuration__label = filters.CharFilter(lookup_expr='iexact')
    configuration = filters.NumberFilter()
    location__label = filters.CharFilter(lookup_expr='iexact')
    location = filters.NumberFilter()
    location__district = filters.CharFilter(lookup_expr='iexact')
    detector_model__label = filters.CharFilter(lookup_expr='iexact')
    detector_model__detector_type = filters.CharFilter(lookup_expr='iexact')
    detector_model = filters.NumberFilter()
    exclude_status = filters.CharFilter(field_name='status', lookup_expr='iexact', exclude=True)
    search = filters.CharFilter(method='filter_search')
    location__location_type = filters.CharFilter(lookup_expr='iexact')
    
    def filter_search(self, queryset, name, value):
        # Search in label and serial
        return queryset.filter(
            models.Q(label__icontains=value) |
            models.Q(serial__icontains=value)
        )

    class Meta:
        model = Detector
        fields = ['search', 'status', 'location', 'detector_model', 'configuration__label', 'exclude_status', 'location__location_type']

class DetectorFaultFilter(filters.FilterSet):
    detector = filters.NumberFilter()
    detector__label = filters.CharFilter(lookup_expr='iexact')
    report_dt_gte = filters.DateFilter(field_name='report_dt', lookup_expr='gte')
    report_dt_lte = filters.DateFilter(field_name='report_dt', lookup_expr='lte')
    report_location__label = filters.CharFilter(lookup_expr='iexact')
    fault_type = filters.CharFilter(lookup_expr='iexact')
    exclude_status = filters.CharFilter(field_name='status', lookup_expr='iexact', exclude=True)

    class Meta:
        model = DetectorFault
        fields = ['detector', 'detector__label', 'report_dt_gte', 'report_dt_lte', 'report_location__label', 'fault_type', 'exclude_status']


class LocationDetectorLogFilter(filters.FilterSet):
    detector = filters.NumberFilter()
    detector__label = filters.CharFilter(lookup_expr='iexact')
    location = filters.NumberFilter()
    location__label = filters.CharFilter(lookup_expr='iexact')
    updated_gte = filters.DateTimeFilter(field_name='updated', lookup_expr='gte')
    updated_lte = filters.DateTimeFilter(field_name='updated', lookup_expr='lte')

    class Meta:
        model = LocationDetectorLog
        fields = [
            'detector', 
            'detector__label', 
            'location', 
            'location__label', 
            'updated_gte', 
            'updated_lte'
        ]
        
class MaintenanceFilter(filters.FilterSet):
    maintenance_type = filters.CharFilter(lookup_expr='iexact')
    status = filters.CharFilter(lookup_expr='iexact')
    detector = filters.NumberFilter()
    detector__label = filters.CharFilter(lookup_expr='iexact')
    detector__detector_model = filters.NumberFilter()
    date_due_lte = filters.DateFilter(field_name='date_due', lookup_expr='lte')
    exclude_status = filters.CharFilter(field_name='status', lookup_expr='iexact', exclude=True)

    class Meta:
        model = Maintenance
        fields = ['maintenance_type', 'status', 'detector', 'detector__label', 'detector__detector_model', 'date_due_lte', 'exclude_status']

class MaintenanceTaskFilter(filters.FilterSet):
    maintenance = filters.NumberFilter()
    maintenance__maintenance_type = filters.CharFilter(lookup_expr='iexact')
    maintenance__detector = filters.NumberFilter()
    maintenance__detector__label = filters.CharFilter(lookup_expr='iexact')
    maintenance__detector__detector_model__detector_type = filters.CharFilter(lookup_expr='iexact')
    maintenance__date_performed_gte = filters.DateFilter(field_name='maintenance__date_performed', lookup_expr='gte')
    maintenance__date_performed_lte = filters.DateFilter(field_name='maintenance__date_performed', lookup_expr='lte')
    task_type = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = MaintenanceTask
        fields = ['maintenance', 'task_type']

class CylinderTypeFilter(filters.FilterSet):
    active = filters.BooleanFilter()

    class Meta:
        model = CylinderType
        fields = ['active']

class CylinderFilter(filters.FilterSet):
    cylinder_number = filters.NumberFilter()
    serial = filters.CharFilter(lookup_expr='icontains')
    location__label = filters.CharFilter(lookup_expr='iexact')
    location = filters.NumberFilter()
    status = filters.CharFilter(lookup_expr='iexact')
    cylinder_type__part_number = filters.CharFilter(lookup_expr='icontains')
    expiry_date_lte = filters.DateFilter(field_name='expiry_date', lookup_expr='lte')
    expiry_date_gte = filters.DateFilter(field_name='expiry_date', lookup_expr='gte')
    exclude_status = filters.CharFilter(field_name='status', lookup_expr='iexact', exclude=True)

    label = filters.CharFilter(method='filter_label')
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Cylinder
        fields = [
            'search',
            'label',
            'serial',
            'location',
            'status',
            'cylinder_type__part_number',
            'expiry_date_lte',
            'expiry_date_gte',
            'exclude_status',
        ]

    def filter_label(self, queryset, name, value):
        value = value.strip().upper()

        if not value:
            return queryset

        if value.startswith('CYL'):
            value = value[3:]

        if not value.isdigit():
            return queryset.none()

        cylinder_number = int(value)

        if cylinder_number <= 0:
            return queryset.none()

        return queryset.filter(cylinder_number=cylinder_number)

    def filter_search(self, queryset, name, value):
        value = value.strip()

        if not value:
            return queryset

        predicate = Q(serial__icontains=value)

        numeric_value = value.upper()

        if numeric_value.startswith('CYL'):
            numeric_value = numeric_value[3:]

        if numeric_value.isdigit():
            cylinder_number = int(numeric_value)

            if cylinder_number > 0:
                predicate |= Q(cylinder_number=cylinder_number)

        return queryset.filter(predicate)

class SensorTypeFilter(filters.FilterSet):
    active = filters.BooleanFilter()
    part_number = filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = SensorType
        fields = ['active', 'part_number']

class SensorFilter(filters.FilterSet):
    serial = filters.CharFilter(lookup_expr='icontains')
    status = filters.CharFilter(lookup_expr='iexact')
    sensor_type = filters.NumberFilter()
    sensor_type__part_number = filters.CharFilter(lookup_expr='icontains')
    detector = filters.NumberFilter()
    detector__label = filters.CharFilter(lookup_expr='iexact')
    detector__serial = filters.CharFilter(lookup_expr='icontains')

    warranty_date_lte = filters.DateFilter(
        field_name='warranty_date',
        lookup_expr='lte'
    )
    warranty_date_gte = filters.DateFilter(
        field_name='warranty_date',
        lookup_expr='gte'
    )

    expiry_date_lte = filters.DateFilter(
        field_name='expiry_date',
        lookup_expr='lte'
    )
    expiry_date_gte = filters.DateFilter(
        field_name='expiry_date',
        lookup_expr='gte'
    )

    exclude_status = filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
        exclude=True
    )

    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(serial__icontains=value) |
            models.Q(sensor_type__part_number__icontains=value)
        )

    class Meta:
        model = Sensor
        fields = [
            'search',
            'serial',
            'status',
            'sensor_type',
            'sensor_type__part_number',
            'detector',
            'detector__label',
            'detector__serial',
            'warranty_date_lte',
            'warranty_date_gte',
            'expiry_date_lte',
            'expiry_date_gte',
            'exclude_status',
        ]
        
class SensorSlotFilter(filters.FilterSet):
    sensor_type__part_number = filters.CharFilter(lookup_expr='icontains')
    detector = filters.NumberFilter()
    detector__label = filters.CharFilter(lookup_expr='iexact')
    detector__serial = filters.CharFilter(lookup_expr='icontains')
    sensorgas = filters.CharFilter(lookup_expr='iexact')
    is_current = filters.BooleanFilter()

    class Meta:
        model = SensorSlot
        fields = ['sensor_type__part_number', 'detector', 'detector__label', 'detector__serial', 'sensorgas', 'is_current']
        
class DetectorModelConfigurationFilter(filters.FilterSet):
    detector_model__label = filters.CharFilter(lookup_expr='iexact')
    detector_model__detector_type = filters.CharFilter(lookup_expr='iexact')
    detector_model = filters.NumberFilter()

    class Meta:
        model = DetectorModelConfiguration
        fields = ['detector_model__label', 'detector_model__detector_type', 'detector_model']

class LocationDetectorSlotFilter(filters.FilterSet):
    location = filters.NumberFilter()
    location__label = filters.CharFilter(lookup_expr='iexact')
    location__location_type = filters.CharFilter(lookup_expr='iexact')
    detector_model = filters.NumberFilter()
    detector_model__label = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = LocationDetectorSlot
        fields = ['location', 'location__label', 'location__location_type', 'detector_model', 'detector_model__label']

class CylinderFaultFilter(filters.FilterSet):
    cylinder = filters.NumberFilter()
    cylinder_label = filters.CharFilter(method="filter_cylinder_label")
    report_dt_gte = filters.DateFilter(field_name="report_dt", lookup_expr="gte")
    report_dt_lte = filters.DateFilter(field_name="report_dt", lookup_expr="lte")
    report_location__label = filters.CharFilter(lookup_expr="iexact")
    fault_type = filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CylinderFault
        fields = [
            "cylinder",
            "cylinder_label",
            "report_dt_gte",
            "report_dt_lte",
            "report_location__label",
            "fault_type",
        ]

    def filter_cylinder_label(self, queryset, name, value):
        value = value.strip().upper()

        if value.startswith("CYL"):
            value = value.replace("CYL", "")

        try:
            cylinder_number = int(value)
        except ValueError:
            return queryset.none()

        return queryset.filter(cylinder__cylinder_number=cylinder_number)
