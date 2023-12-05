"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Team

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

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
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

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
    """Form enabling users to change their password."""

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
    """Form enabling unregistered users to sign up."""

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

'''
haroon code here

we need to make a form we can use to create teams
'''

class UsernameInputField(forms.CharField):
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
    '''
    form to create team
    '''
    class Meta:
        '''
        form options
        '''
        model = Team
        fields = ['team_name','team_description']

    team_name = forms.CharField(max_length=50, label="Team name")
    team_description = forms.CharField(required=False, label="Team nescription")
    team_members = UsernameInputField(label = "Input usernames of team members (with @ infront of usernames)")

    def clean(self):
        '''
        this just checks that the usernames given are real
        and gives error message if not real
        '''
        super().clean()
        team_name = self.cleaned_data.get('team_name')
        team_description = self.cleaned_data.get('team_description')

        usernames = self.cleaned_data.get('team_members')
        number_of_team_members = len(usernames)
        i = 0

        while (i < number_of_team_members and User.objects.filter(username = usernames[i]).exists()):
            i+=1
        if (i != number_of_team_members-1):
            usernames = None
            self.add_error('team_members', "Invalid user in team")

    def save(self):
        super().save(commit=False)
        data = self.cleaned_data
        team = Team.objects.create(team_name = data["team_name"], team_description = data["team_description"])
        for usr in data["team_members"]:
            user = User.objects.get(username = usr)
            team.team_members.add(user)
        return team