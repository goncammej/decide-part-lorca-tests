from base.tests import BaseTestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from .forms import ClassicForm


class CreateClassicViewTest(BaseTestCase):
    def test_get_request(self):
        response = self.client.get(reverse("create_classic"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "configurator/create_classic.html")
        self.assertIsInstance(response.context["form"], ClassicForm)

    def test_post_request_valid_form(self):
        data = {
            "name": "Test Voting",
            "desc": "This is a test voting",
            "question_desc": "This is a test question",
            "option1": "Option 1",
            "option2": "Option 2",
            "more_options": "Option 3\nOption 4",
        }
        response = self.client.post(reverse("create_classic"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("manage_census"))

        self.assertEqual(self.client.session["voting_id"], 1)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Classic voting created successfully!")

    def test_post_request_invalid_form(self):
        data = {
            "name": "",  # Empty name
            "desc": "This is a test voting",
            "question_desc": "This is a test question",
            "option1": "Option 1",
            "option2": "Option 2",
            "more_options": "Option 3\nOption 4",
        }
        response = self.client.post(reverse("create_classic"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "configurator/create_classic.html")

        form = response.context["form"]

        self.assertFalse(form.is_valid())
