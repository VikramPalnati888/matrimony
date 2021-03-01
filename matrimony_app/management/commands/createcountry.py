from django.core.management.base import BaseCommand

from matrimony_app.models import Country


class Command(BaseCommand):
    help = "Enter the country details"

    @staticmethod
    def handle(*args, **options):
        print("Creating Countries...")
        countries = ['india','USA', ]
        Country.objects.all().delete()
        print('All countries are deleted')
        index = 0
        while index < len(countries):
            country_obj = Country()
            country_obj.country = countries[index]
            country_obj.save()
            index += 1
        print('Successfully created countries.')
