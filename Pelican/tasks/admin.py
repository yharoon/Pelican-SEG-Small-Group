from django.contrib import admin
from tasks.models import User,Team,Task,Invitation,Notification

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Task)
admin.site.register(Invitation)
admin.site.register(Notification)