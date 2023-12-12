from django.core.management.base import BaseCommand, CommandError
from tasks.models import User, Team, Task

class Command(BaseCommand):
    """Custom Django management command to remove all data from the database."""

    help = 'Removes all seeded data from the database'

    def handle(self, *args, **options):
        """Handle method called when the command is run to unseed the database."""

        # Delete all User objects from the database
        User.objects.filter().delete()

        # Delete all Team objects from the database
        Team.objects.filter().delete()

        # Delete all Task objects from the database
        Task.objects.filter().delete()
