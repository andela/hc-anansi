from hc.api.models import Check
from hc.test import BaseTestCase
from datetime import timedelta as td
from django.utils import timezone


class MyChecksTestCase(BaseTestCase):

    def setUp(self):
        super(MyChecksTestCase, self).setUp()
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()

    def test_it_works(self):
        for email in ("alice@example.org", "bob@example.org"):
            self.client.login(username=email, password="password")
            r = self.client.get("/checks/")
            self.assertContains(r, "Alice Was Here", status_code=200)

    def test_it_shows_green_check(self):
        self.check.last_ping = timezone.now()
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-up")

        # Mobile
        self.assertContains(r, "label-success")

    def test_it_shows_red_check(self):
        self.check.last_ping = timezone.now() - td(days=3)
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-down")

        # Mobile
        self.assertContains(r, "label-danger")

    def test_it_shows_amber_check(self):
        self.check.last_ping = timezone.now() - td(days=1, minutes=30)
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/")

        # Desktop
        self.assertContains(r, "icon-grace")

        # Mobile
        self.assertContains(r, "label-warning")

    def test_it_shows_unresolved_check(self):
        '''Check that an unresolved check tab, table and list appear when
        there is an unresolved check'''
        self.check.last_ping = timezone.now() - td(days=3)
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        response = self.client.get("/checks/")

        # Check it contains the unresolved checks tab id
        self.assertContains(response, 'id="unresolved-checks"')

        # Desktop
        self.assertContains(response, "unresolved-checks-table")

        # Mobile
        self.assertContains(response, "unresolved-checks-list")

    def test_it_shows_no_unresolved_check_message(self):
        '''Check that no unresolved checks message is shown if user has
        no unresolved checks'''
        self.check.last_ping = timezone.now() - td(days=1)
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        response = self.client.get("/checks/")

        # Check it contains the unresolved checks tab id
        self.assertContains(response, "You don't have any unresolved checks")