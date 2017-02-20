from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from checker.tasks.base import (result, sum, get)

api = {
    'process': {
        'get': '/api/process/get/'
    }
}

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class AuthTest(TestCase):
    def setUp(self):
        self.user, _ = User.objects.get_or_create(username='user1')
        self.user.set_password('pass1')
        self.user.save()

    def test_login(self):
        login = self.client.login(username=self.user.username, password='pass1')
        self.assertTrue(login)

class TasksTest(TestCase):
    def test_async(self):
        task = sum.s(2, 2).delay()
        self.assertTrue(task)

    def test_async_result(self):
        task = sum.s(2, 2).delay()
        self.assertEqual(task.get(), 4)

class ClientTest(TestCase):
    def test_request(self):
        response = self.client.get(api.get('process').get('get'), {})
        self.assertEqual(response.status_code, 200)
