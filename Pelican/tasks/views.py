from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, TeamForm
from tasks.helpers import login_prohibited
from .models import User, Team
from django.shortcuts import get_object_or_404
from .models import Task
from .forms import TaskForm
from django.http import HttpResponseRedirect

@login_required
def dashboard(request):
    current_user = request.user
    print(current_user)  # Add this line for debugging

    team_form = TeamForm(request.POST or None)

    if request.method == 'POST' and team_form.is_valid():
        new_team = team_form.save()
        new_team.members.add(current_user)
        new_team.save()
        return redirect('dashboard')

    # Fetching teams associated with the current user
    user_teams = Team.objects.filter(members=current_user)
    print(user_teams)  # Add this line for debugging

    return render(request, 'dashboard.html', {'user': current_user, 'team_form': team_form, 'user_teams': user_teams})

from django.shortcuts import get_object_or_404
from .models import Task

def team_detail(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    task_form = TaskForm(request.POST or None)
    
    if request.method == 'POST' and task_form.is_valid():
        new_task = task_form.save(commit=False)
        new_task.team = team
        new_task.save()
        task_form.save_m2m()  # Save many-to-many relationships
        
        # Redirect to the team detail page after creating the task
        return HttpResponseRedirect(request.path_info)
        
    team_tasks = Task.objects.filter(team=team)
    
    return render(request, 'team_detail.html', {'team': team, 'team_tasks': team_tasks, 'task_form': task_form})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

class TeamCreateView(LoginRequiredMixin, FormView):
    """Display team creation screen and handle team creation."""

    template_name = 'team.html'
    form_class = TeamForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()  # Get all users from the database
        return context

    def form_valid(self, form):
        team_name = form.cleaned_data['name']
        selected_members = form.cleaned_data['members']

        new_team = Team.objects.create(name=team_name)
        new_team.members.add(*selected_members)
        
        # Add the current user to the team
        new_team.members.add(self.request.user)
        
        team_members = new_team.members.all()

        # Redirect to the team detail page after creating the team
        return HttpResponseRedirect(reverse('team_detail', args=[new_team.id]))
