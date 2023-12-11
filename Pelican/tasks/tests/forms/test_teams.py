from django.test import TestCase
from django.contrib.auth.hashers import get_user_model
from tasks.models import Team
from django.core.exceptions import ValidationError

User = get_user_model()

class TeamModelTest(TestCase):

    def setUp(self):
        # Create some user instances for testing
        self.user1 = User.objects.create(username='janedoe', email='janedoe@example.com')
        self.user2 = User.objects.create(username='janedoej', email='janedoej@example.com')

    def test_create_team_with_unique_name(self):
        team = Team.objects.create(name='Team pelican')
        self.assertEqual(team.name, 'Team pelican')

    def test_create_team_with_duplicate_name(self):
        Team.objects.create(name='Team pelican1')
        with self.assertRaises(ValidationError):
            Team.objects.create(name='Team pelican1')

    def test_adding_members_to_team(self):
        team = Team.objects.create(name='Team pelican2')
        team.members.add(self.user1, self.user2)
        self.assertIn(self.user1, team.members.all())
        self.assertIn(self.user2, team.members.all())

    def test_removing_members_from_team(self):
        team = Team.objects.create(name='Team pelican3')
        team.members.add(self.user1, self.user2)
        team.members.remove(self.user1)
        self.assertNotIn(self.user1, team.members.all())

    def test_team_name_length_validation(self):
        long_name = 'x' * 101
        with self.assertRaises(ValidationError):
            Team.objects.create(name=long_name)

    def test_user_membership_in_multiple_teams(self):
        team1 = Team.objects.create(name='Team pelican4')
        team2 = Team.objects.create(name='Team pelican5')
        team1.members.add(self.user1)
        team2.members.add(self.user1)
        self.assertIn(self.user1, team1.members.all())
        self.assertIn(self.user1, team2.members.all())
