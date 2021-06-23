from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError
from main_platform.models import RomeCode, TradeToRomeCode
import csv
import os


class Command(BaseCommand):
    help = """fulfill database fields with rome codes and their different names
              using csv file"""

    def handle(self, *args, **options):
        path = os.getcwd()
        i = 0
        with open(os.path.join(path, 'main_platform', 'management', 'commands', 'csv', 'rome_codes_names.csv'),
                  mode="r", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                with transaction.atomic():
                    code_exist = RomeCode.objects.filter(code__icontains=row['ROME_PROFESSION_CARD_CODE']).exists()
                    if code_exist:
                        pass
                    else:
                        RomeCode.objects.create(code=row['ROME_PROFESSION_CARD_CODE'])
        with open(os.path.join(path, 'main_platform', 'management', 'commands', 'csv', 'rome_codes_names.csv'),
                  mode="r", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                with transaction.atomic():
                    rc = RomeCode.objects.filter(code__icontains=row['ROME_PROFESSION_CARD_CODE'])[0]
                    trc = TradeToRomeCode.objects.create(job_name=row['ROME_PROFESSION_NAME'], job_code=rc)
