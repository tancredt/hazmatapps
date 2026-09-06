import csv
import os
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Export database models to CSV files compatible with import_csv.py"

    def add_arguments(self, parser):
        parser.add_argument(
            "--prefix",
            default="inventory",
            help="CSV filename prefix (e.g. 'inventory' or 'stuff')",
        )
        parser.add_argument(
            "--dir",
            default="csv_export",
            help="Directory to save CSV files",
        )

    def handle(self, *args, **options):
        prefix = options["prefix"]
        export_dir = options["dir"]
        
        # Create the export directory if it doesn't exist
        os.makedirs(export_dir, exist_ok=True)

        # Import order respects foreign-key dependencies
        model_order = [
            "stuff.District",
            "stuff.Location",
            "stuff.DetectorModel",
            "stuff.DetectorModelConfiguration",
            "stuff.LocationDetectorSlot",
            "stuff.Detector",
            "stuff.SensorType",
            "stuff.Sensor",
            "stuff.SensorSlot",
            "stuff.Maintenance",
            "stuff.MaintenanceTask",
            "stuff.DetectorFault",
            "stuff.CylinderType",
            "stuff.Cylinder",
            "stuff.CylinderFault",
            "stuff.LocationDetectorLog",
        ]

        for model_path in model_order:
            self.export_model(model_path, prefix, export_dir)

        self.stdout.write(self.style.SUCCESS("\n✅ Export complete!"))

    def export_model(self, model_path, prefix, export_dir):
        app_label, model_name = model_path.split(".")
        csv_name = f"{prefix}_{model_name.lower()}.csv"
        csv_path = os.path.join(export_dir, csv_name)
        
        model = apps.get_model(model_path)
        fields = model._meta.fields
        headers = [f.name for f in fields]
        
        self.stdout.write(f"Exporting {model_path} → {csv_name}")
        
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            count = 0
            for obj in model.objects.all().iterator():
                row = {}
                for field in fields:
                    # For ForeignKeys, get the raw ID (attname) to ensure compatibility
                    if field.is_relation:
                        val = getattr(obj, field.attname)
                    else:
                        val = getattr(obj, field.name)
                    
                    row[field.name] = "" if val is None else val
                writer.writerow(row)
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f"  → Exported {count} rows"))
