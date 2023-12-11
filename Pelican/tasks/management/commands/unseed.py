from django.core.management.base import BaseCommand, CommandError
from tasks.models import User,Team,Task

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.filter().delete()
        Team.objects.filter().delete()
        Task.objects.filter().delete()