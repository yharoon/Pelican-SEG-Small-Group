"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Team
from .models import Task

class LogInForm(forms.Form):
   
    """
    Form for logging in users.
    Contains fields for username and password.
    Includes a method to authenticate the user.
    """
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """
    Form for updating user profile information.
    Based on the User model and allows updating of fields like first name, last name, username, and email.
    """

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """
    Mixin form for handling new password creation.
    Includes fields for new password and password confirmation with custom validation.
    Ensures that the password and confirmation match.
    """

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """
    Form enabling users to change their password.
    Inherits from NewPasswordMixin and adds a field for the current password.
    Includes validation to authenticate the current password.
    """
    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    
    """
    Form for new user registration.
    Inherits from NewPasswordMixin.
    Based on the User model.
    Allows setting of user attributes and password during sign-up stage.
    """
    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user


class UsernameInputField(forms.CharField):
    """
    Custom form field for username input.
    Processes the input to remove spaces and split at '@'.
    Prepares the value for display and data handling.
    """
 
    def to_python(self, value):
        if value in self.empty_value:
            return self.empty_value
        value = str(value).replace(" ","").split("@")
        if self.strip:
            value = [i.strip for i in value]
        return value

    def prepare_value(self,value):
        if value is None:
            return None
        return "@".join([str(i) for i in value])

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'members']

class TaskForm(forms.ModelForm):
    """
    Form for creating or updating tasks.
    Based on the Task model and allows 
    setting of task attributes like name, description, due date, and assignees.
    """
    
    class Meta:
        model = Task
        fields = ['name', 'description', 'due_date', 'assigned_to']

class InviteForm(forms.Form):
    """
    Form for inviting users to a team.
    Contains a field for selecting multiple users.
    Initializes with a query set of users who are not already members of the team.
    
    """
    users = forms.ModelMultipleChoiceField(queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team')
        super().__init__(*args, **kwargs)
        self.fields['users'].queryset = User.objects.exclude(teams=team)
