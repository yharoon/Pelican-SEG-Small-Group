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
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, TeamForm, TaskForm
from tasks.helpers import login_prohibited
from .models import User, Team, Task, Invitation, Notification
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q

@login_required
def dashboard(request):
    current_user = request.user
    user_tasks = Task.objects.filter(assigned_to=current_user)
    team_form = TeamForm(request.POST or None)

    if request.method == 'POST' and team_form.is_valid():
        new_team = team_form.save()
        new_team.members.add(current_user)
        new_team.save()
        return redirect('dashboard')

    # Fetching teams associated with the current user
    user_teams = Team.objects.filter(members=current_user)

    # Fetch notifications associated with the current user directly using Notification model
    user_notifications = Notification.objects.filter(user=current_user)

    return render(
        request,
        'dashboard.html',
        {'user': current_user, 
        'team_form': team_form, 
        'user_teams': user_teams, 
        'user_tasks': user_tasks, 
        'user_notifications': user_notifications}
    )

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

def remove_member(request, team_id, member_id):
    team = get_object_or_404(Team, pk=team_id)
    member_to_remove = get_object_or_404(User, pk=member_id)

    if request.method == 'POST' and team.has_team_leader_perms(request.user):
        team.members.remove(member_to_remove)
        return HttpResponseRedirect(reverse('team_detail', args=[team_id]))

    else:
        messages.add_message(request, messages.ERROR, "Only Team Leaders can remove members, You are not a Team Leader")

    return render(request, 'confirm_remove_member.html', {'team': team, 'member_to_remove': member_to_remove})

def clear_received_invitations(request):
    # Get the invitations sent to the current user
    received_invitations = request.user.received_invitations.all()

    # Delete all invitations sent to the current user
    for invitation in received_invitations:
        invitation.delete()

    # Redirect to the dashboard or any appropriate page after clearing received invitations
    return redirect('dashboard')

def reset_user_data(request):
    # Deleting User's Teams
    user_teams = request.user.teams.all()
    for team in user_teams:
        team.delete()

    # Deleting Sent Invitations
    sent_invitations = request.user.sent_invitations.all()
    for invitation in sent_invitations:
        invitation.delete()

    # Removing User from Received Invitations
    received_invitations = request.user.received_invitations.all()
    for invitation in received_invitations:
        invitation.receiver.remove(request.user)

    # Redirect to the dashboard or any appropriate page
    return redirect('dashboard')  # Change 'dashboard' to your desired URL name

def send_invitations(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    if request.method == 'POST':
        selected_user_ids = request.POST.getlist('selected_users')
        selected_users = User.objects.filter(pk__in=selected_user_ids)

        for user in selected_users:
            # Create an invitation for each selected user to join the team
            invitation = Invitation.objects.create(sender=request.user, receiver=user, team=team)
    
            # Create a notification for the invited user and associate it with the invitation
            notification = Notification.objects.create(user=user, message=f"Click here to join ", invitation=invitation)

        messages.success(request, 'Invitations sent successfully!')
        return redirect('team_detail', team_id=team_id)
    else:
        # Fetch users who are not already in the team
        users_not_in_team = User.objects.exclude(id__in=team.members.all().values_list('id', flat=True))

        return render(request, 'invite_members.html', {'team': team, 'users_not_in_team': users_not_in_team})

def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    invitation.accept()
    return redirect('dashboard')  # Redirect to appropriate page after accepting

def reject_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    invitation.decline()
    return redirect('dashboard')  # Redirect to appropriate page after rejecting

def confirm_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)

    if request.method == 'POST':
        if 'accept' in request.POST:
            # Accept the invitation
            invitation.accept()
        elif 'reject' in request.POST:
            # Reject the invitation
            invitation.decline()

        # Delete the associated notification
        try:
            notification = Notification.objects.get(invitation=invitation)
            notification.delete()
        except Notification.DoesNotExist:
            # Handle if the notification doesn't exist
            raise Http404("Notification does not exist")

        return redirect('dashboard')  # Redirect to the dashboard or any appropriate page

    return render(request, 'confirm_invitation.html', {'invitation': invitation})

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
        search_term = self.request.GET.get('userSearch')
        if search_term:
            users = User.objects.filter(
                Q(username__icontains=search_term) | 
                Q(first_name__icontains=search_term) | 
                Q(last_name__icontains=search_term)
            )
        else:
            users = User.objects.all()
        context['users'] = users
        return context

    def form_valid(self, form):
        team_name = form.cleaned_data['name']
        selected_members = form.cleaned_data['members']
        team_leader = self.request.user

        new_team = Team.objects.create(name=team_name)
        new_team.members.add(*selected_members)
        new_team.team_leader.add(team_leader)
        
        # Add the current user to the team
        new_team.members.add(self.request.user)
        
        team_members = new_team.members.all()

        # Redirect to the team detail page after creating the team
        return HttpResponseRedirect(reverse('team_detail', args=[new_team.id]))