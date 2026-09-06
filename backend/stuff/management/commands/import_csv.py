import csv
import os
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction, models
from django.apps import apps


class Command(BaseCommand):
    help = "Import CSV files into the database using Django ORM."

    def add_arguments(self, parser):
        parser.add_argument(
            "--prefix",
            default="inventory",
            help="CSV filename prefix (e.g. 'inventory' or 'stuff')",
        )
        parser.add_argument(
            "--dir",
            default="csv_import",
            help="Directory containing CSV files",
        )
        parser.add_argument(
            "--reset-sequences",
            action="store_true",
            help="Reset PostgreSQL auto-increment sequences after import",
        )

    def handle(self, *args, **options):
        self.prefix = options["prefix"]
        self.csv_dir = options["dir"]

        # Import order respects foreign-key dependencies
        self.model_order = [
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

        for model_path in self.model_order:
            self.import_model(model_path)

        if options["reset_sequences"]:
            self.reset_sequences()

        self.stdout.write(self.style.SUCCESS("\n✅ Import complete!"))

    def import_model(self, model_path):
        app_label, model_name = model_path.split(".")
        csv_name = f"{self.prefix}_{model_name.lower()}.csv"
        csv_path = os.path.join(self.csv_dir, csv_name)

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.WARNING(f"Skip  {csv_name} (not found)"))
            return

        model = apps.get_model(model_path)
        field_map = self.get_field_map(model)

        self.stdout.write(f"Load  {csv_name} → {model_path}")

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                self.stdout.write(self.style.WARNING("  Empty file"))
                return

            valid_cols, skipped_cols = self.validate_columns(reader.fieldnames, field_map)

            if skipped_cols:
                self.stdout.write(f"  Ignore columns: {skipped_cols}")

            if not valid_cols:
                self.stdout.write(self.style.ERROR("  No valid columns"))
                return

            success = 0
            errors = 0

            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):
                    try:
                        data = self.convert_row(row, valid_cols, field_map)
                        model.objects.create(**data)
                        success += 1
                    except Exception as e:
                        errors += 1
                        if errors <= 5:
                            self.stdout.write(self.style.ERROR(f"  Row {row_num}: {e}"))

            status = "OK" if errors == 0 else f"{errors} ERR"
            self.stdout.write(self.style.SUCCESS(f"  → {success} rows ({status})"))

    def get_field_map(self, model):
        field_map = {}
        for field in model._meta.fields:
            field_map[field.name] = field
            field_map[field.attname] = field
        return field_map

    def validate_columns(self, csv_columns, field_map):
        valid = {}
        skipped = []
        for col in csv_columns:
            col = col.strip()
            if col in field_map:
                field = field_map[col]
                valid[col] = field.attname
            else:
                skipped.append(col)
        return valid, skipped

    def convert_row(self, row, valid_cols, field_map):
        data = {}
        for csv_col, orm_col in valid_cols.items():
            raw = row.get(csv_col, "").strip()
            field = field_map[csv_col]
            converted = self.convert_value(raw, field)
            if converted is not None or not self.is_nullable(field):
                data[orm_col] = converted
        return data

    def is_nullable(self, field):
        return field.null and not getattr(field, "empty_strings_allowed", True)

    def convert_value(self, raw, field):
        if raw == "":
            if isinstance(field, (models.CharField, models.TextField)):
                return ""
            return None

        if isinstance(field, (models.AutoField, models.BigAutoField, models.IntegerField)):
            return int(raw)

        if isinstance(field, models.DecimalField):
            return Decimal(raw)

        if isinstance(field, models.BooleanField):
            return raw.lower() in ("1", "true", "t", "yes", "on")

        if isinstance(field, models.DateField):
            return self.parse_date(raw)

        if isinstance(field, models.DateTimeField):
            return self.parse_datetime(raw)

        if isinstance(field, models.ForeignKey):
            return int(raw)

        return raw

    def parse_date(self, value):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"bad date: {value}")

    def parse_datetime(self, value):
        for fmt in (
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"bad datetime: {value}")

    def reset_sequences(self):
        self.stdout.write("\nReset sequences...")
        from django.db import connection

        with connection.cursor() as cursor:
            for model_path in self.model_order:
                model = apps.get_model(model_path)
                table = model._meta.db_table
                try:
                    cursor.execute(
                        "SELECT pg_get_serial_sequence(%s, %s)", [table, "id"]
                    )
                    result = cursor.fetchone()
                    if result and result[0]:
                        cursor.execute(f"SELECT COALESCE(MAX(id),0) FROM {table}")
                        max_id = cursor.fetchone()[0]
                        if max_id:
                            cursor.execute(
                                f"SELECT setval(%s, %s, true)", [result[0], max_id]
                            )
                            self.stdout.write(f"  {table}: {max_id}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  {table}: {e}"))
