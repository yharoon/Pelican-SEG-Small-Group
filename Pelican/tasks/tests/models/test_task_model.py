"""Test for Task Model"""

from django.core.exceptions import ValidationError, IntegrityError
from django.test import TestCase
from tasks.models import Task

class TaskModelTestCase(TestCase):
	"""
	reusing ammended json for teams/tasks
	this time we use it 
	"""
	'''
	Unit Tests for Task Model
	'''

	fixtures = [
        'tasks/tests/fixtures/users_for_teams_tasks.json',
    ]

	def setUp(self):
	'''
	set up team, team members in that team, and adds them
	then we can set up a task and test on this
	'''
		self.team = Team.objects.create(name = "temp_team_name")
		self.team_members = User.objects.all()
		self.assigned_to = User.objects.get(username = "@petrapickles")
		self.team.members.add(*self.team_members)
		self.description = "description"
		self.due_date = "2024-10-10"
		self.name = "temp_task_name"
		self.task = Task.objects.create(description = self.description,
										nama = self.name,
										due_date = self.due_date,
										team = self.team,
										)
		self.task.assigned_to.add(self.assigned_to)

	def test_description_can_be_blank(self):
		self.description = ""
		self._assert_task_is_valid()

	def test_description_is_too_large(self):
		self.description = "a"*256
		self._assert_task_is_invalid()

	def test_description_isnt_too_large(self):
		self.description = "a"*254
		self._assert_task_is_valid()

	def test_due_date_cant_be_blank(self):
		self.due_date = ""
		self._assert_task_is_invalid()

	def test_name_must_be_unique(self):
		with self.assertRaises(IntegrityError):
			Task.objects.create(
				name = "temp_task_name",
				team = self.team,
			)

	def test_name_is_too_large(self):
		self.name = "a"*101
		self._assert_task_is_invalid()

	def test_name_isnt_too_large(self):
		self.name = "k"*99
		self._assert_task_is_valid()

	def test_task_team_integrity(self):
		"""
		tests that when a team is deleted, tasks are also
		deleted
		deleted all team objects then checks that there
		should be no task objects
		"""
		Team.objects.all().delete()
		self.assertEqual(0,Task.objects.count())

	def test_model_str(self):
		assertEqual(str(self.task), self.description)

	def _assert_task_is_valid(self):
		try:
			self.task.full_clean()
		except (ValidationError):
			self.fail('Test team should be valid')

	def _assert_task_is_invalid(self):
		with self.assertRaises(ValidationError):
			self.task.full_clean()