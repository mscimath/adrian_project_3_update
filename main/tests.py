from django.test import TestCase


class BasicTests(TestCase):
    def test_homepage_status(self):
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 302])
