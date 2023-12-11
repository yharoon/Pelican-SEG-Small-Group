from django import forms
from django.test import TestCase
from tasks.forms import TaskForm
from tasks.models import User, Team, Task

class TaskFormTestCase(TestCase):
	'''
	Unit Test for Task Form
	'''

	fixtures = ['tasks/tests/fixtures/other_users.json']
	#fixtures for a couple users

	def setUp(self):
	'''
	used to create changing objects (Tasks)
	every test func gets a fresh version of
	this setup
	'''
		self.team_members = User.objects.get(first_name = "John")
		self.user = User.objects.get(username = "@petrapickles")
		self.team = Team.objects.create(name = "temp_team_name", members = self.team_members)
		self.form_input = {"name":"temp_task_name", "description":"description", 
							"due_date":"01-01-2024", "assigned_to":self.team_members,
							"team":self.team}

	def test_form_has_necessary_fields(self):
		form = TaskForm()
		self.assertIn("name", form.fields)
		self.assertIn("description", form.fields)
		self.assertIn("due_date", form.fields)
		self.assertIn("assigned_to", form.fields)
		self.assertIn("team", form.fields)

	def test_form_accepts_valid_input(self):
		form = TaskForm(data = self.form_input, instance = self.user)
		self.assertTrue(form.is_valid())

	def test_form_rejects_long_description(self):
		self.form_input["description"] = "a"*256
		form = TaskForm(data = self.form_input)
		self.assertFalse(form.is_valid())

	def test_form_rejects_long_name(self):
		self.form_input["name"] = "a"*101
		form = TaskForm(data = self.form_input)
		self.assertFalse(form.is_valid())

	def test_task_needs_description(self):
		self.form_input["description"] = ""
		form = TaskForm(data = self.form_input)
		self.assertFalse(form.is_valid())

	def test_task_needs_due_date(self):
		self.form_input["due_date"] = ""
		form = TaskForm(data = self.form_input)
		self.assertFalse(form.is_valid())

	def test_task_needs_team(self):
		self.form_input["team"] = ""
		form = TaskForm(data = self.form_input)
		self.assertFalse(form.is_valid())

	def test_task_needs_assigned_to(self):
		self.form_input["assigned_to"] = ""
		form = TaskForm(data = self.form_input)
		self.assertFalse(form.is_valid())

	def test_task_doesnt_need_name(self):
		self.form_input["name"] = ""
		form = TaskForm(data = self.form_input)
		self.assertTrue(form.is_valid())

	def test_task_saves_correctly(self):
		form - TaskForm(data = self.form_input, instance = self.user)
		before_count = Task.objects.count()
		form.save()
		after_count = Task.objects.count()
		task = Task.objects.get(name = self.form_input["name"])
		self.assertEqual(before_count, after_count)
		self,assertEqual(task.name, self.form_input["name"])
		self,assertEqual(task.description, self.form_input["description"])
		self,assertEqual(task.assigned_to, self.form_input["assigned_to"])
		self,assertEqual(task.due_date, self.form_input["due_date"])
		self,assertEqual(task.team, self.form_input["team"])