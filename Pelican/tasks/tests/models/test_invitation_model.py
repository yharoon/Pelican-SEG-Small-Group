
class TestModelInvitationCase(TestCase):

    fixtures = [
        'tasks/tests/fixtures/users_for_teams_tasks.json',
    ]

    def setUp(self):
        self.sender = User.objects.get(username = '@johndoe')
        self.receiver = User.objects.get(username = '@janedoe')
        self.team = Team.objects.create(name = "temp_team_name", team_leader = self.user)
        self.team_members = User.objects.all()
        self.accepted = False
        self.invitation = Invitation.objects.create(sender = self.sender,receiver = self.receiver,team = self.team, accepted = self.accepted)


    def test_invitation_team_integrity(self):
        """
        tests when a team is deleted, invitations are also 
        deleted
        deleted all team objects then checks that there 
        should be no task objects
        """
        Team.objects.all().delete()
        self.assertEqual(0,Invitation.objects.count())


    def test_accept_works(self):
        self.invitation.accept()
        accepted_invitation = Invitation.objects.get(id = self.invitation.id)
        self.assertTrue(accepted_invitation.accepted)

    def test_decline_works(self):
        self.invitation.decline()
        declined_invitation = Invitation.objects.get(id = self.invitation.id)
        self.assertFalse(declined_invitation.accepted)
