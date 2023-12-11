from django.core.management.base import BaseCommand
from tasks.models import User, Team, Task
from faker import Faker
from random import randint

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 10
    TEAM_COUNT = 10
    TASK_COUNT = 10
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_teams()
        self.teams = Team.objects.all()
        self.create_tasks()
        self.tasks = Task.objects.all()
        self.makeAdmin()

    def create_teams(self):
        self.generate_fixture_team()
        self.generate_random_teams()

    def generate_fixture_team(self):
        team = Team.objects.create(name = "fixture_team_prime")
        team.members.add(User.objects.get(username = "@johndoe"))
        team.members.add(User.objects.get(username = "@janedoe"))
        team.members.add(User.objects.get(username = "@charlie"))

    def generate_random_teams(self):
        team_count = Team.objects.count()
        counter = 0
        while team_count < self.TEAM_COUNT:
            print(f"Seeding team {team_count}/{self.TEAM_COUNT}", end='\r')
            self.generate_team(counter)
            team_count = Team.objects.count()
            counter += 1
        print("Team seeding complete.")

    def generate_team(self, counter):
        name = "Epsilon:" + self.faker.first_name() + "_team_" + str(counter)
        random_members = randint(5,self.USER_COUNT)
        random_start = randint(0,self.USER_COUNT-random_members)
        team_members = self.users[random_start:random_members+random_start]
        self.try_create_team({"name":name, "members":team_members})

    def try_create_team(self, data):
        try:
            self.create_team(data)
        except:
            pass

    def create_team(self, data):
        team = Team.objects.create(
            name = data["name"],
            )
        team.members.add(*data["members"])

    def create_tasks(self):
        task_count = Task.objects.count()
        while task_count < self.TASK_COUNT:
            print(f"Seeding task {task_count}/{self.TASK_COUNT}", end='\r')
            self.generate_task()
            task_count = Task.objects.count()
        print("Task seeding complete.")

    def generate_task(self):
        """
        random_team = randint(0,self.TEAM_COUNT)
        team_from = self.teams[random_team]
        assigned_to = team_from.members
        name = self.faker.last_name() + "_task"
        descrption = "See "+self.faker.email()
        due_date = self.faker.date()
        """
        team_from = self.teams[0]
        assigned_to = team_from.members
        name = "_task"
        descrption = "See "
        due_date = "01-01-2024"
        print("in generate_task")
        self.try_create_task({"team":team_from, 
                            "assigned_to":assigned_to,
                            "name":name,
                            "descrption":descrption,
                            "due_date":due_date})

    def try_create_task(self, data):
        try:
            print("in try_create_task")
            self.create_task(data)
        except:
            print("except")
            pass

    def create_task(self, data):
        print("in create_task")
        task = Task.objects.create(
            name = data["name"],
            descrption = data["descrption"],
            due_date = data["due_date"],
            )
        task.team.add(data["team"])
        task.assigned_to.add(*data["assigned_to"])

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
