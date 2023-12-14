from django.core.management.base import BaseCommand
from tasks.models import User, Team, Task
from faker import Faker
from random import randint,sample

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 5
    TEAM_COUNT = 5
    TASK_COUNT = 5
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.makeAdmin()
        self.users = User.objects.all()
        self.all_usernames = list(User.objects.values_list("username"))
        self.create_teams()
        self.teams = Team.objects.all()
        self.all_team_names = list(Team.objects.values_list("name"))
        self.create_tasks()

    def create_tasks(self):
        task_count = 0
        while task_count < self.TASK_COUNT:
            print(f"Seeding task {task_count}/{self.TASK_COUNT}", end='\r')
            self.generate_task()
            task_count = Task.objects.count()
        print("Task seeding complete.")

    def generate_task(self):
        due_date = self.faker.date()
        number_of_tasks = randint(1,10)
        team_from = sample(self.all_team_names,1)
        team = Team.objects.get(name = team_from[0][0])
        id_list = list(Team.objects.all().filter(name = team_from[0][0]).values("members"))
        member_list = list()
        for member in id_list:
            member_list.append(User.objects.get(id = member["members"]))
        number_assigned_to = randint(1,len(member_list))
        assigned_to = sample(member_list, number_assigned_to)
        name = "task_name_" + str(Task.objects.count())
        description = name + " - no description"
        data = {
        "name" : name,
        "team_from" : team_from,
        "assigned_to" : assigned_to,
        "description" : description,
        "due_date" : due_date
        }
        self.try_create_task(data)

    def try_create_task(self, data):
        try:
            self.create_task(data)
        except:
            pass

    def create_task(self,data):
        generate_task = Task.objects.create(
                        due_date = data["due_date"],
                        name = data["name"],
                        description = data["description"],
                        team = Team.objects.get(name = data["team_from"][0][0]),
                        )
        for members in data["assigned_to"]:
            generate_task.assigned_to.add(User.objects.get(username = members))

    def create_teams(self):
        self.generate_user_teams()
        self.generate_random_teams()

    def generate_user_teams(self):
        fixture_team = Team.objects.create(name = "fixture_team")
        fixture_team.members.add(User.objects.get(username = "@johndoe"))
        fixture_team.members.add(User.objects.get(username = "@janedoe"))
        fixture_team.members.add(User.objects.get(username = "@charlie"))

    def generate_random_teams(self):
        team_count = 0
        while team_count < self.TEAM_COUNT:
            print(f"Seeding team {team_count}/{self.TEAM_COUNT}", end='\r')
            self.generate_team()
            team_count = Team.objects.count()
        print("Team seeding complete.")

    def generate_team(self):
        number_of_members = randint(1,self.USER_COUNT)
        team_members = sample(self.all_usernames, number_of_members)
        team_leader = sample(self.all_usernames, 1)[0][0]
        team_name = team_leader + "_team"
        self.try_create_team({"team_name":team_name,
                            "team_members":team_members})

    def try_create_team(self,data):
        try:
            self.create_team(data)
        except:
            pass

    def create_team(self,data):
        generate_team = Team.objects.create(
            name = data["team_name"])
        for member in data["team_members"]:
            generate_team.members.add(User.objects.get(username = member[0]))

    def makeAdmin(self):
        self.admin = User.objects.get(username = "@johndoe")
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return f"{first_name.lower()}.{last_name.lower()}@example.org"
