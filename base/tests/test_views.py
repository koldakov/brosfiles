from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase


class RobotsCase(TestCase):
    def setUp(self):
        self.url = reverse('robots')

    def test_get(self):
        response = self.client.get(self.url)
        lines = response.content.decode().splitlines()

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(lines[0], 'User-Agent: *')

    def test_post(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
