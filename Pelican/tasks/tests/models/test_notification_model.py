from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from django.test import TestCase
from tasks.models import User,Team,Invitation,Notification

class NotificationModelTestCase(TestCase):

    fixtures = [
        'tasks/tests/fixtures/users_for_teams_tasks.json',
    ]
    
    def setUp(self):
        self.user = User.objects.get(username = '@johndoe')
        self.message = "message"
        self.created_at = models.DateTimeField(auto_now_add = True)
        self.now_time = models.DateTimeField(auto_now_add = True)
        self.team = Team.objects.create(name = "name",members =User.objects.all,team_leader = User.objects.get(username = '@janedoe') )
        self.invitation = Invitation.objects.create(sender = User.objects.get(username = '@janedoe',receiver = self.user),team = self.team,accepted = False)
        
    
    def test_notification_message_is_too_long(self):
        self.message = "a"*256
        self.assert_task_is_invalid()
    
    def test_notifcation_isnt_too_large(self):
          self.message = "a"*244
          self._assert_task_is_valid()
    
    def test_invitation_notification_integrity(self):
        """
		tests that when a invitation is deleted, notification is also
		deleted
		deleted all invitation objects then checks that there
		should be no notification objects
		"""
        Invitation.objects.all().delete()
        self.assertEqual(0,Notification.objects.count())

    def test_user_notification_integrity(self):
        """
		tests that when a user is deleted, notifications are also
		deleted
		deleted all user objects then checks that there
		should be no notification objects
		"""
        User.objects.all().delete()
        self.assertEqual(0,Notification.objects.count())
    
    def test_created_at_date_time(self):
          self.assertEqual(self.created_at,self.now_time)
    
    def _assert_task_is_valid(self):
        try:
            self.task.full_clean()
        except (ValidationError):
            self.fail('Test team should be valid')
    
    def _assert_task_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.task.full_clean()
