from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from django_filters import rest_framework as filters
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from weasyprint import HTML
from django.db import models, transaction
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from .serializers import PerformSwapSerializer
from .models import (
    District,
    Location,
    DetectorModel,
    Detector,
    SensorType,
    Sensor,
    SensorSlot,
    Maintenance,
    MaintenanceTask,
    DetectorFault,
    Cylinder,
    CylinderType,
    CylinderFault,
    CylinderGas,
    LocationDetectorSlot,
    LocationDetectorLog,
    LocationType,
    Manufacturer,
    DetectorType,
    DetectorModelConfiguration,
    Supplier,
    DetectorStatus,
    MaintenanceType,
    MaintenanceTaskType,
    MaintenanceStatus,
    DetectorFaultType,
    CylinderUnit,
    CylinderVolume,
    CylinderStatus,
    SensorStatus,
    SensorGas
)
from .serializers import (
    DistrictChoiceSerializer,
    LocationSerializer,
    DetectorModelSerializer,
    DetectorSerializer,
    DetectorModelConfigurationSerializer,
    MaintenanceSerializer,
    MaintenanceTaskSerializer,
    DetectorFaultSerializer,
    CylinderSerializer,
    CylinderTypeSerializer,
    CylinderFaultSerializer,
    LocationDetectorSlotSerializer,
    LocationDetectorLogSerializer,
    SensorTypeSerializer,
    SensorSerializer,
    SensorSlotSerializer,
    LocationTypeChoiceSerializer,
    ManufacturerChoiceSerializer,
    DetectorTypeChoiceSerializer,
    SupplierChoiceSerializer,
    DetectorStatusChoiceSerializer,
    MaintenanceTypeChoiceSerializer,
    MaintenanceTaskTypeChoiceSerializer,
    MaintenanceStatusChoiceSerializer,
    DetectorFaultTypeChoiceSerializer,
    CylinderGasChoiceSerializer,
    CylinderUnitChoiceSerializer,
    CylinderVolumeChoiceSerializer,
    CylinderStatusChoiceSerializer,
    SensorStatusChoiceSerializer,
    SensorGasChoiceSerializer,
    ChangeDetectorLocationSerializer,
    ChangeCylinderLocationSerializer,
    DetectorLabelOnlySerializer,
    DetectorLocationStatusUpdateSerializer,
)
from .filters import (
    LocationFilter,
    DetectorModelFilter,
    DetectorFilter,
    DetectorFaultFilter,
    DetectorModelConfigurationFilter,
    MaintenanceFilter,
    MaintenanceTaskFilter,
    CylinderFilter,
    CylinderTypeFilter,
    CylinderFaultFilter,
    LocationDetectorSlotFilter,
    LocationDetectorLogFilter,
    SensorTypeFilter,
    SensorFilter,
    SensorSlotFilter,
)


################---Choice Views---#################


class LocationTypeView(APIView):
    def get(self, request):
        choices = LocationType.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = LocationTypeChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class ManufacturerView(APIView):
    def get(self, request):
        choices = Manufacturer.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = ManufacturerChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class DetectorTypeView(APIView):
    def get(self, request):
        choices = DetectorType.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = DetectorTypeChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class SupplierView(APIView):
    def get(self, request):
        choices = Supplier.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = SupplierChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class DetectorStatusView(APIView):
    def get(self, request):
        choices = DetectorStatus.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = DetectorStatusChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class CylinderStatusView(APIView):
    def get(self, request):
        choices = CylinderStatus.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = CylinderStatusChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class SensorStatusView(APIView):
    def get(self, request):
        choices = SensorStatus.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = SensorStatusChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class MaintenanceTypeView(APIView):
    def get(self, request):
        choices = MaintenanceType.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = MaintenanceTypeChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class MaintenanceTaskTypeView(APIView):
    def get(self, request):
        choices = MaintenanceTaskType.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = MaintenanceTaskTypeChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class MaintenanceStatusView(APIView):
    def get(self, request):
        choices = MaintenanceStatus.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = MaintenanceStatusChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class DetectorFaultTypeView(APIView):
    def get(self, request):
        choices = DetectorFaultType.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = DetectorFaultTypeChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class CylinderUnitView(APIView):
    def get(self, request):
        choices = CylinderUnit.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = CylinderUnitChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class CylinderGasView(APIView):
    def get(self, request):
        choices = CylinderGas.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = CylinderGasChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class CylinderVolumeView(APIView):
    def get(self, request):
        choices = CylinderVolume.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = CylinderVolumeChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class SensorGasView(APIView):
    def get(self, request):
        choices = SensorGas.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = SensorGasChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


class DistrictView(APIView):
    def get(self, request):
        choices = District.choices
        choice_list = [{'value': value, 'label': label} for value, label in choices]
        serializer = DistrictChoiceSerializer(choice_list, many=True)
        return Response(serializer.data)


##################---Main Views---##########################


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LocationFilter


class DetectorModelViewSet(viewsets.ModelViewSet):
    serializer_class = DetectorModelSerializer
    queryset = DetectorModel.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DetectorModelFilter


class DetectorViewSet(viewsets.ModelViewSet):
    serializer_class = DetectorSerializer
    queryset = Detector.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DetectorFilter


class MaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceSerializer
    queryset = Maintenance.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MaintenanceFilter


class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceTaskSerializer
    queryset = MaintenanceTask.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MaintenanceTaskFilter


class DetectorFaultViewSet(viewsets.ModelViewSet):
    serializer_class = DetectorFaultSerializer
    queryset = DetectorFault.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DetectorFaultFilter


class CylinderTypeViewSet(viewsets.ModelViewSet):
    serializer_class = CylinderTypeSerializer
    queryset = CylinderType.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CylinderTypeFilter


class CylinderViewSet(viewsets.ModelViewSet):
    serializer_class = CylinderSerializer
    queryset = Cylinder.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CylinderFilter


class SensorTypeViewSet(viewsets.ModelViewSet):
    serializer_class = SensorTypeSerializer
    queryset = SensorType.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SensorTypeFilter


class SensorViewSet(viewsets.ModelViewSet):
    serializer_class = SensorSerializer
    queryset = Sensor.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SensorFilter


class SensorSlotViewSet(viewsets.ModelViewSet):
    serializer_class = SensorSlotSerializer
    queryset = SensorSlot.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SensorSlotFilter


class DetectorModelConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = DetectorModelConfigurationSerializer
    queryset = DetectorModelConfiguration.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DetectorModelConfigurationFilter


class LocationDetectorSlotViewSet(viewsets.ModelViewSet):
    serializer_class = LocationDetectorSlotSerializer
    queryset = LocationDetectorSlot.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LocationDetectorSlotFilter


class LocationDetectorLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for viewing detector location change logs.
    """
    serializer_class = LocationDetectorLogSerializer
    queryset = LocationDetectorLog.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LocationDetectorLogFilter


class CylinderFaultViewSet(viewsets.ModelViewSet):
    serializer_class = CylinderFaultSerializer
    queryset = CylinderFault.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CylinderFaultFilter


# ============== PDF Report Views ==============


def get_date_context():
    today = timezone.now().date()
    eight_weeks = today + timedelta(weeks=8)
    return {'today': today, 'eight_weeks': eight_weeks}


@login_required
def detectors_pdf(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    detector_model = request.GET.get('detector_model', '')
    location = request.GET.get('location', '')
    configuration = request.GET.get('configuration', '')
    show_decommissioned = request.GET.get('show_decommissioned', 'false').lower() == 'true'
    sort_key = request.GET.get('sort_key', 'label')
    sort_direction = request.GET.get('sort_direction', 'asc')
    sort_field_map = {
        'label': 'label',
        'serial': 'serial',
        'model': 'detector_model__label',
        'location': 'location__label',
        'status': 'status',
        'configuration': 'configuration__label',
        'firmware': 'firmware',
        'purchase_date': 'purchase_date',
        'location_updated': 'location_updated',
    }
    sort_field = sort_field_map.get(sort_key, 'label')
    if sort_direction.lower() == 'desc':
        sort_field = f'-{sort_field}'

    detectors = Detector.objects.select_related(
        'detector_model', 'location', 'configuration'
    ).order_by(sort_field)

    if search:
        detectors = detectors.filter(
            models.Q(label__icontains=search) | models.Q(serial__icontains=search)
        )
    if status:
        detectors = detectors.filter(status=status)
    if detector_model:
        detectors = detectors.filter(detector_model=detector_model)
    if location:
        detectors = detectors.filter(location=location)
    if configuration:
        detectors = detectors.filter(configuration=configuration)
    if not show_decommissioned:
        detectors = detectors.exclude(status='DC')

    context = {
        'detectors': detectors,
        'filters': {
            'search': search,
            'status': status,
            'detector_model': detector_model,
            'location': location,
            'configuration': configuration,
            'show_decommissioned': show_decommissioned,
            'sort_key': sort_key,
            'sort_direction': sort_direction,
        },
        **get_date_context()
    }

    html_string = render_to_string('inventory/pdf/detectors.html', context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="detectors.pdf"'
    return response


@login_required
def sensors_pdf(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    sensor_type = request.GET.get('sensor_type', '')
    detector = request.GET.get('detector', '')
    expiry_date_lte = request.GET.get('expiry_date_lte', '')
    show_decommissioned = request.GET.get('show_decommissioned', 'false').lower() == 'true'
    sort_key = request.GET.get('sort_key', 'serial')
    sort_direction = request.GET.get('sort_direction', 'asc')
    sort_field_map = {
        'serial': 'serial',
        'sensor_type': 'sensor_type__part_number',
        'sensorgas': 'sensor_type__sensorgas',
        'detector': 'detector__label',
        'status': 'status',
        'order_date': 'order_date',
        'receive_date': 'receive_date',
        'warranty_date': 'warranty_date',
        'expiry_date': 'expiry_date',
    }
    sort_field = sort_field_map.get(sort_key, 'serial')
    if sort_direction.lower() == 'desc':
        sort_field = f'-{sort_field}'

    sensors = Sensor.objects.select_related('sensor_type', 'detector').order_by(sort_field)

    if search:
        sensors = sensors.filter(
            models.Q(serial__icontains=search) | models.Q(sensor_type__part_number__icontains=search)
        )
    if status:
        sensors = sensors.filter(status=status)
    if sensor_type:
        sensors = sensors.filter(sensor_type=sensor_type)
    if detector:
        sensors = sensors.filter(detector=detector)
    if expiry_date_lte:
        sensors = sensors.filter(expiry_date__lte=expiry_date_lte)
    if not show_decommissioned:
        sensors = sensors.exclude(status='DC')

    context = {
        'sensors': sensors,
        'filters': {
            'search': search,
            'status': status,
            'sensor_type': sensor_type,
            'detector': detector,
            'expiry_date_lte': expiry_date_lte,
            'show_decommissioned': show_decommissioned,
            'sort_key': sort_key,
            'sort_direction': sort_direction,
        },
        **get_date_context()
    }

    html_string = render_to_string('inventory/pdf/sensors.html', context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sensors.pdf"'
    return response


@login_required
def cylinders_pdf(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    cylinder_type = request.GET.get('cylinder_type', '')
    location = request.GET.get('location', '')
    expiry_date_lte = request.GET.get('expiry_date_lte', '')
    show_empty = request.GET.get('show_empty', 'false').lower() == 'true'
    sort_key = request.GET.get('sort_key', 'label')
    sort_direction = request.GET.get('sort_direction', 'asc')
    sort_field_map = {
        'label': 'cylinder_number',
        'serial': 'serial',
        'cylinder_type': 'cylinder_type__part_number',
        'supplier': 'cylinder_type__supplier',
        'detector': 'detector__label',
        'location': 'location__label',
        'status': 'status',
        'order_date': 'order_date',
        'receive_date': 'receive_date',
        'expiry_date': 'expiry_date',
    }
    sort_field = sort_field_map.get(sort_key, 'cylinder_number')
    if sort_direction.lower() == 'desc':
        sort_field = f'-{sort_field}'

    cylinders = Cylinder.objects.select_related('cylinder_type', 'location', 'detector').order_by(sort_field)

    if search:
        query = models.Q(serial__icontains=search)
        cleaned_search = search.strip().upper()
        if cleaned_search.startswith("CYL"):
            cleaned_search = cleaned_search.replace("CYL", "")
        if cleaned_search.isdigit():
            query |= models.Q(cylinder_number=int(cleaned_search))
        cylinders = cylinders.filter(query)
    if status:
        cylinders = cylinders.filter(status=status)
    if cylinder_type:
        cylinders = cylinders.filter(cylinder_type=cylinder_type)
    if location:
        cylinders = cylinders.filter(location=location)
    if expiry_date_lte:
        cylinders = cylinders.filter(expiry_date__lte=expiry_date_lte)
    if not show_empty:
        cylinders = cylinders.exclude(status='MT')

    context = {
        'cylinders': cylinders,
        'filters': {
            'search': search,
            'status': status,
            'cylinder_type': cylinder_type,
            'location': location,
            'expiry_date_lte': expiry_date_lte,
            'show_empty': show_empty,
            'sort_key': sort_key,
            'sort_direction': sort_direction,
        },
        **get_date_context()
    }

    html_string = render_to_string('inventory/pdf/cylinders.html', context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cylinders.pdf"'
    return response


@login_required
def maintenance_pdf(request):
    status = request.GET.get('status', '')
    maintenance_type = request.GET.get('maintenance_type', '')
    detector = request.GET.get('detector', '')
    detector_model = request.GET.get('detector__detector_model', '')
    date_due_lte = request.GET.get('date_due_lte', '')
    show_complete = request.GET.get('show_complete', 'false').lower() == 'true'
    sort_key = request.GET.get('sort_key', 'date_due')
    sort_direction = request.GET.get('sort_direction', 'asc')
    sort_field_map = {
        'maintenance_type': 'maintenance_type',
        'status': 'status',
        'detector': 'detector__label',
        'detector_label': 'detector__label',
        'detector_model': 'detector__detector_model__label',
        'date_due': 'date_due',
        'date_performed': 'date_performed',
    }
    sort_field = sort_field_map.get(sort_key, 'date_due')
    if sort_direction.lower() == 'desc':
        sort_field = f'-{sort_field}'

    maintenances = Maintenance.objects.select_related('detector').prefetch_related('tasks').order_by(sort_field)

    if status:
        maintenances = maintenances.filter(status=status)
    if maintenance_type:
        maintenances = maintenances.filter(maintenance_type=maintenance_type)
    if detector:
        maintenances = maintenances.filter(detector=detector)
    if detector_model:
        maintenances = maintenances.filter(detector__detector_model=detector_model)
    if date_due_lte:
        maintenances = maintenances.filter(date_due__lte=date_due_lte)
    if not show_complete:
        maintenances = maintenances.exclude(status='CL')

    context = {
        'maintenances': maintenances,
        'filters': {
            'status': status,
            'maintenance_type': maintenance_type,
            'detector': detector,
            'detector_model': detector_model,
            'date_due_lte': date_due_lte,
            'show_complete': show_complete,
            'sort_key': sort_key,
            'sort_direction': sort_direction,
        },
        **get_date_context()
    }

    html_string = render_to_string('inventory/pdf/maintenance.html', context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="maintenance.pdf"'
    return response


@login_required
def faults_pdf(request):
    status = request.GET.get('status', '')
    fault_type = request.GET.get('fault_type', '')
    detector = request.GET.get('detector', '')
    report_dt_lte = request.GET.get('report_dt_lte', '')
    show_closed = request.GET.get('show_closed', 'false').lower() == 'true'
    sort_key = request.GET.get('sort_key', 'report_dt')
    sort_direction = request.GET.get('sort_direction', 'desc')
    sort_field_map = {
        'detector': 'detector__label',
        'fault_type': 'fault_type',
        'status': 'status',
        'report_dt': 'report_dt',
        'report_location': 'report_location__label',
        'resolve_dt': 'resolve_dt',
    }
    sort_field = sort_field_map.get(sort_key, 'report_dt')
    if sort_direction.lower() == 'desc':
        sort_field = f'-{sort_field}'

    faults = DetectorFault.objects.select_related('detector', 'report_location').order_by(sort_field)

    if status:
        faults = faults.filter(status=status)
    if fault_type:
        faults = faults.filter(fault_type=fault_type)
    if detector:
        faults = faults.filter(detector=detector)
    if report_dt_lte:
        faults = faults.filter(report_dt__lte=report_dt_lte)
    if not show_closed:
        faults = faults.exclude(status='CL')

    context = {
        'faults': faults,
        'filters': {
            'status': status,
            'fault_type': fault_type,
            'detector': detector,
            'report_dt_lte': report_dt_lte,
            'show_closed': show_closed,
            'sort_key': sort_key,
            'sort_direction': sort_direction,
        },
        **get_date_context()
    }

    html_string = render_to_string('inventory/pdf/faults.html', context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="faults.pdf"'
    return response


@login_required
def detector_detail_pdf(request, detector_id):
    from django.shortcuts import get_object_or_404
    detector = get_object_or_404(
        Detector.objects.select_related('detector_model', 'location', 'configuration'),
        id=detector_id
    )
    sensor_slots = SensorSlot.objects.select_related('sensor__sensor_type').filter(detector=detector, is_current=True).order_by('sensorgas')
    maintenances = Maintenance.objects.filter(detector=detector).order_by('-date_due')
    faults = DetectorFault.objects.filter(detector=detector).order_by('-report_dt')

    context = {
        'detector': detector,
        'sensor_slots': sensor_slots,
        'maintenances': maintenances,
        'faults': faults,
        **get_date_context()
    }

    html_string = render_to_string('inventory/pdf/detector_detail.html', context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="detector_{detector.label}.pdf"'
    return response


##################################################################
###################  These are for the changing locations app  #######
################################################################


class DetectorLabelOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DetectorLabelOnlySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DetectorFilter

    def get_queryset(self):
        return Detector.objects.select_related('location')


class DetectorLocationStatusUpdateView(APIView):
    """
    Restricted endpoint to update only the location and status of detectors.
    Accepts a single object or a list of objects for atomic updates.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if isinstance(data, dict):
            data = [data]

        serializer = DetectorLocationStatusUpdateSerializer(data=data, many=True)
        if serializer.is_valid():
            with transaction.atomic():
                for item in serializer.validated_data:
                    try:
                        detector = Detector.objects.select_for_update().get(id=item['detector_id'])
                        detector.location_id = item['location_id']
                        detector.status = item['status']
                        detector.save(update_fields=['location', 'status'])
                    except Detector.DoesNotExist:
                        return Response(
                            {"error": f"Detector {item['detector_id']} not found"},
                            status=status.HTTP_404_NOT_FOUND
                        )
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerformSwapView(APIView):
    """
    Atomic endpoint to perform a detector swap and create a fault report simultaneously.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PerformSwapSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        fault_data = data.pop('fault_data')

        try:
            with transaction.atomic():
                DetectorFault.objects.create(**fault_data)

                removed_det = Detector.objects.select_for_update().get(id=data['removed_detector_id'])
                removed_det.location_id = data['removed_location_id']
                removed_det.status = data['removed_status']
                removed_det.save(update_fields=['location', 'status'])

                replacement_det = Detector.objects.select_for_update().get(id=data['replacement_detector_id'])
                replacement_det.location_id = data['replacement_location_id']
                replacement_det.status = data['replacement_status']
                replacement_det.save(update_fields=['location', 'status'])

        except Detector.DoesNotExist as e:
            return Response({"error": f"Detector not found: {e}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": True}, status=status.HTTP_200_OK)
