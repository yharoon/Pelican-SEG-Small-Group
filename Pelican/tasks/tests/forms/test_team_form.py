from django import forms
from django.test import TestCase
from django.http import HttpRequest
from tasks.forms import TeamForm
from tasks.models import User, Team

class TeamFormTestCase(TestCase):
	'''
	Unit Test for Team Form
	'''

	fixtures = ['tasks/tests/fixtures/other_users.json']
	#fixtures for a couple users


	def setUp(self):
	'''
	used to create changing objects (Team)
	every test func gets a fresh version of
	this setup
	'''
		self.team_members = User.objects.get(first_name = "John")
		self.user = User.objects.get(username = "@petrapickles")
		self.form_input = {"name" : "temp_team_name", "members" : self.user.pk}

	def test_form_has_necessary_fields(self):
		form = TeamForm()
		self.assertIn("name", form.fields)
		self.assertIn("members", form.fields)

	def test_takes_valid_input(self):
		request = HttpRequest()
		request.POST = {
			"name": "temo_team_name",
			"members": self.user.pk,
		}

		form = TeamForm(request.POST, members = user)
		self.assertTrue(form.is_valid())

	def test_form_uses_model_validation(self):
		form = TeamForm(data = self.form_input)
		form.save()
		form2 = TeamForm(data = self.form_input)
		self.assertFalse(form2.is_valid())

	def test_form_saves_correctly(self):
		form = TeamForm(instance = self.user, data = self.form_input)
		before_count = Team.objects.count()
		form.save()
		after_count = Team.objects.count()
		team = Team.objects.get(name = self.form_input["name"])
		self.assertEqual(before_count, after_count)
		self.assertEqual(team.name, "temp_team_name")
		self.assertEqual(team.members, self.team_members)