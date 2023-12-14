from django.test import TestCase
from tasks.models import User, Team, Invitation
from tasks.forms import PasswordForm
from django import forms
from django.http import HttpRequest
from django.conf import settings

class InviteFormTestCase(TestCase):
	