# myapp/management/commands/fill_languages.py

from django.core.management.base import BaseCommand
from accounts.models import Language

class Command(BaseCommand):
    help = 'Fill languages in the database'

    def handle(self, *args, **options):
        languages = [
            'English',
            'Krio',
            'Mende',
            'Temne',
            'Limba',
            'Fula',
            'Kuranko',
            'Mandinka',
            'Kissi',
            'Gola',
            'Susu',
            'Yalunka',
            'Bambara',
            'Sherbro',
            'Borom',
            'French',
            'Spanish',
            'Mandarin Chinese',
            'Arabic',
            'Portuguese',
            'German',
            'Italian',
            'Russian',
            'Japanese',
            'Korean',
        ]

        for language in languages:
            Language.objects.get_or_create(name=language)

        self.stdout.write(self.style.SUCCESS('Languages filled successfully'))