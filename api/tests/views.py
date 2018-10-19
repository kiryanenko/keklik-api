from django.test import TestCase


class SchemeTestCase(TestCase):
    def testGetScheme(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
