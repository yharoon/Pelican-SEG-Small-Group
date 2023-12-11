"""Test for Team Model"""

from django.core.exceptions import ValidationError, IntegrityError
from django.test import TestCase
from tasks.models import Team

class TeamModelTestCase(TestCase):
	"""
	a note, users_for_teams_tasks.json is a modified json
	of user data to let me quickly add users to a
	temp team, first 3 users in the json all have
	the name John
	"""
	'''
	Unit Tests for Team Model
	'''

    fixtures = [
        'tasks/tests/fixtures/users_for_teams_tasks.json',
    ]

	def setUp(self):
		'''
		set up team, team members in that team, and adds them
		'''
		self.team = Team.objects.create(name = "temp_team_name")
		self.team_members = User.objects.get(first_name = "John")
		self.team.members.add(*self.team_members)

	def test_unique_team_name_is_enforced(self):
		with self.assertRaises(IntegrityError):
			Team.objects.create(
				name = "temp_team_name"
			)

	def test_team_members_are_added(self):
		assertEqual(self.team_members, self.team.members)

	def test_team_name_is_too_large(self):
		self.team.name = "k"*101
		self._assert_team_is_invalid()

	def test_team_name_isnt_too_large(self):
		self.team.name = "k"*99
		self._assert_team_is_valid()

	def test_model_str(self):
		assertEqual(str(self.team), "temp_team_name")

	def _assert_team_is_valid(self):
		try:
			self.team.full_clean()
		except (ValidationError):
			self.fail('Test team should be valid')

	def _assert_team_is_invalid(self):
		with self.assertRaises(ValidationError):
			self.team.full_clean()