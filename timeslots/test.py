from django.test import TestCase


class WSGITest(TestCase):
    def test_application_object(self):
        from .wsgi import application
        from django.core.handlers.wsgi import WSGIHandler
        self.assertTrue(isinstance(application, WSGIHandler))
