"""Tests for the TeamCreate view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TeamForm
from tasks.models import User, Team
from tasks.tests.helpers import reverse_with_next

class TeamCreateViewTest(TestCase):

    fixtures = ['tasks/tests/fixtures/users_for_teams_tasks.json']

    def setUp(self):
		self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe2',
            'username': '@johndoe2',
            'email': 'johndoe2@example.org',
        }
        self.url = reverse("team")
        self.user = User.objects.get(username='@johndoe')
        self.team_members = User.objects.get(first_name = "John")
        self.team = Team.objects.create(name = "temp_team_name")
        self.team.members.add(*self.team_members)

    def test_team_url(self):
    	self.assertEqual(self.url, "/team/")

    #def test_get_team(self):