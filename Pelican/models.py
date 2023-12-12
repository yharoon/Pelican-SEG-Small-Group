from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar.
           Default size is set to 120 pixels.
        """
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
       
        """Returns a smaller version of the user's Gravatar (60 pixels)."""
        return self.gravatar(size=60)

class Team(models.Model):
    
    """
    Model representing a team.
    Contains team name and members.
    """
    
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(User, related_name='teams', null=True)

    def __str__(self):
        """String representation of the team model."""  
        return self.name

class Task(models.Model):
    """
    Model for tasks assigned to teams.
    Includes description, due date, associated team, and assignees.
    """
    description = models.CharField(max_length=255)
    due_date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks')
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        """String representation of the task model."""
        return self.description

class Invitation(models.Model):
    """
    Model for managing team invitations.
    Tracks sender, receiver, associated team, and acceptance status.
    
    """
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_invitations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    def accept(self):
        """Method to handle invitation acceptance."""
        self.receiver.teams.add(self.team)
        self.accepted = True
        self.save()

    def decline(self):
        """Method to handle invitation decline."""
        self.accepted = False
        self.save()

class Notification(models.Model):
    """
    Model for user notifications.
    Includes the user, message content, creation date, and related invitation (if any).
    """    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, related_name='related_notification', null=True, blank=True)

    
    def __str__(self):
        """String representation of the notification model."""
        
        return f"{self.user.username}: {self.message}"
