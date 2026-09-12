from rest_framework import serializers
from django.db import transaction
from .models import (
    District,
    Location,
    DetectorModel,
    Detector,
    DetectorModelConfiguration,
    LocationDetectorSlot,
    Maintenance,
    MaintenanceTask,
    DetectorFault,
    CylinderType,
    Cylinder,
    CylinderFault,
    LocationType,
    Manufacturer,
    DetectorType,
    Supplier,
    DetectorStatus,
    MaintenanceType,
    MaintenanceTaskType,
    MaintenanceStatus,
    DetectorFaultType,
    CylinderGas,
    CylinderUnit,
    CylinderStatus,
    SensorGas,
    SensorType,
    Sensor,
    SensorStatus,
    SensorSlot,
    LocationDetectorLog
)


###################---Choice Serializers---###################


class LocationTypeChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class ManufacturerChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class DetectorTypeChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class SupplierChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class DetectorStatusChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class MaintenanceTypeChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class MaintenanceTaskTypeChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class MaintenanceStatusChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class DetectorFaultTypeChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class CylinderGasChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class CylinderVolumeChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class CylinderUnitChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class CylinderStatusChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class SensorStatusChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class SensorGasChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class DistrictChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


#################---Main Serializers---#####################


class LocationSerializer(serializers.ModelSerializer):
    district = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Location
        fields = [
            "id",
            "label",
            "address",
            "location_type",
            "priority",
            "district",
        ]


class DetectorModelSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(allow_null=True, required=False)
    supplier = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = DetectorModel
        fields = "__all__"
        read_only_fields = []


class DetectorSerializer(serializers.ModelSerializer):
    purchase_date = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = Detector
        fields = "__all__"
        read_only_fields = ['location_updated']

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        label = attrs.get('label')
        if label:
            if instance and instance.label != label:
                if Detector.objects.filter(label=label).exists():
                    raise serializers.ValidationError({'label': ['A detector with this label already exists.']})
            elif not instance:
                if Detector.objects.filter(label=label).exists():
                    raise serializers.ValidationError({'label': ['A detector with this label already exists.']})

        serial = attrs.get('serial')
        if serial:
            if instance and instance.serial != serial:
                if Detector.objects.filter(serial=serial).exists():
                    raise serializers.ValidationError({'serial': ['A detector with this serial already exists.']})
            elif not instance:
                if Detector.objects.filter(serial=serial).exists():
                    raise serializers.ValidationError({'serial': ['A detector with this serial already exists.']})

        required_fields = ['detector_model', 'status', 'location']
        for field in required_fields:
            if not attrs.get(field):
                raise serializers.ValidationError({field: [f'{field.replace("_", " ").title()} is required.']})

        purchase_cost = attrs.get('purchase_cost')
        if purchase_cost is not None and purchase_cost < 0:
            raise serializers.ValidationError({'purchase_cost': ['Purchase cost cannot be negative.']})

        purchase_date = attrs.get('purchase_date')
        if purchase_date:
            from datetime import date
            if purchase_date > date.today():
                raise serializers.ValidationError({'purchase_date': ['Purchase date cannot be in the future.']})

        return attrs

    def create(self, validated_data):
        detector = super().create(validated_data)
        if detector.configuration_id is not None:
            sync_detector_sensor_slots(detector)
        return detector

    def update(self, instance, validated_data):
        old_configuration_id = instance.configuration_id
        detector = super().update(instance, validated_data)
        if detector.configuration_id != old_configuration_id:
            sync_detector_sensor_slots(detector)
        return detector


class DetectorModelConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectorModelConfiguration
        fields = "__all__"


class MaintenanceSerializer(serializers.ModelSerializer):
    date_due = serializers.DateField(allow_null=True, required=False)
    date_performed = serializers.DateField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    detector_model = serializers.SerializerMethodField()
    detector_label = serializers.SerializerMethodField()

    class Meta:
        model = Maintenance
        fields = ['id', "maintenance_type", "status", "detector", "detector_label", "detector_model", "date_due", "date_performed", "performed_by", "notes", "created_at", "updated_at"]

    def get_detector_model(self, obj):
        if obj.detector:
            return obj.detector.detector_model_id
        return None

    def get_detector_label(self, obj):
        if obj.detector:
            return obj.detector.label
        return None


class LocationDetectorSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationDetectorSlot
        fields = "__all__"


class LocationDetectorLogSerializer(serializers.ModelSerializer):
    new_location_label = serializers.CharField(source="new_location.label", read_only=True)
    new_location_district = serializers.CharField(source="new_location.district", read_only=True)
    old_location_label = serializers.CharField(source="old_location.label", read_only=True, allow_null=True)
    old_location_district = serializers.CharField(source="old_location.district", read_only=True, allow_null=True)
    detector_label = serializers.CharField(source="detector.label", read_only=True)

    class Meta:
        model = LocationDetectorLog
        fields = [
            "id",
            "new_location",
            "new_location_label",
            "new_location_district",
            "old_location",
            "old_location_label",
            "old_location_district",
            "detector",
            "detector_label",
            "updated"
        ]
        read_only_fields = fields


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTask
        fields = "__all__"


class DetectorFaultSerializer(serializers.ModelSerializer):
    report_dt = serializers.DateTimeField(allow_null=True, required=False)
    resolve_dt = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = DetectorFault
        fields = "__all__"


class CylinderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CylinderType
        fields = "__all__"


class CylinderSerializer(serializers.ModelSerializer):
    order_date = serializers.DateField(allow_null=True, required=False)
    receive_date = serializers.DateField(allow_null=True, required=False)
    expiry_date = serializers.DateField(allow_null=True, required=False)
    operational_date = serializers.DateField(allow_null=True, required=False)
    empty_date = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = Cylinder
        exclude = ['cylinder_number']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['label'] = f"CYL{instance.cylinder_number:05d}"
        return data

    def create(self, validated_data):
        from django.db import models as db_models
        with transaction.atomic():
            last_cylinder = Cylinder.objects.select_for_update().aggregate(db_models.Max('cylinder_number'))
            next_number = (last_cylinder['cylinder_number__max'] or 0) + 1
            validated_data['cylinder_number'] = next_number
            return super().create(validated_data)


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = "__all__"


class SensorSerializer(serializers.ModelSerializer):
    order_date = serializers.DateField(allow_null=True, required=False)
    receive_date = serializers.DateField(allow_null=True, required=False)
    warranty_date = serializers.DateField(allow_null=True, required=False)
    expiry_date = serializers.DateField(allow_null=True, required=False)
    install_date = serializers.DateField(allow_null=True, required=False)
    remove_date = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = Sensor
        fields = "__all__"


class SensorSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorSlot
        fields = "__all__"


class ChangeDetectorLocationSerializer(serializers.Serializer):
    detector_id = serializers.IntegerField()
    location_id = serializers.IntegerField()


class ChangeCylinderLocationSerializer(serializers.Serializer):
    cylinder_id = serializers.IntegerField()
    location_id = serializers.IntegerField()


class CylinderFaultSerializer(serializers.ModelSerializer):
    report_dt = serializers.DateTimeField(read_only=True)
    resolve_dt = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = CylinderFault
        fields = "__all__"


def sync_detector_sensor_slots(detector):
    """
    Sync a detector's sensor slots with its configuration.
    """
    if detector.configuration is None:
        return

    gas_string = detector.configuration.sensor_gases or ""
    valid_gases = {value for value, _ in SensorGas.choices}

    gases = []
    for gas in gas_string.split(","):
        gas = gas.strip()
        if gas and gas in valid_gases and gas not in gases:
            gases.append(gas)

    if not gases:
        return

    with transaction.atomic():
        SensorSlot.objects.filter(detector=detector).update(is_current=False)
        for gas in gases:
            slot = (
                SensorSlot.objects
                .filter(detector=detector, sensorgas=gas)
                .order_by("id")
                .first()
            )
            if slot:
                slot.is_current = True
                slot.save(update_fields=["is_current"])
            else:
                SensorSlot.objects.create(
                    detector=detector,
                    sensorgas=gas,
                    sensor=None,
                    is_current=True,
                )


####################################################################
# These are for the changing locations app
####################################################################


class DetectorLabelOnlySerializer(serializers.ModelSerializer):
    location_label = serializers.CharField(source='location.label', read_only=True)
    location_district = serializers.CharField(source='location.district', read_only=True)

    class Meta:
        model = Detector
        fields = ['id', 'label', 'location_label', 'location_district']
        read_only_fields = fields


class DetectorLocationStatusUpdateSerializer(serializers.Serializer):
    detector_id = serializers.IntegerField()
    location_id = serializers.IntegerField()
    status = serializers.CharField(max_length=2)


class PerformSwapSerializer(serializers.Serializer):
    removed_detector_id = serializers.IntegerField()
    removed_location_id = serializers.IntegerField()
    removed_status = serializers.CharField(max_length=2)
    replacement_detector_id = serializers.IntegerField()
    replacement_location_id = serializers.IntegerField()
    replacement_status = serializers.CharField(max_length=2)
    fault_data = DetectorFaultSerializer()
