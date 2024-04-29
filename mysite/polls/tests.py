import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """ should return false for any future dated pub_dates """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
        time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """ should return false for any dates > 1 day old """
        now = timezone.now()
        time = now - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """ should return true for any dates now => 1 day old """
        now = timezone.now()
        valid_question = Question(pub_date=now)
        self.assertIs(valid_question.was_published_recently(), True)
        time = now - datetime.timedelta(days=1)
        valid_question = Question(pub_date=time)
        self.assertIs(valid_question.was_published_recently(), True)
        time = now - datetime.timedelta(days=.5)
        valid_question = Question(pub_date=time)
        self.assertIs(valid_question.was_published_recently(), True)

from django.urls import reverse

def create_question(question_text, days):
    """ Test helper for generating questions """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """ Should display the 'no questions' message """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_published_questions(self):
        """ Questions with a pub_date <= now() are considered to be published and should appear """
        q1 = create_question("Text",0)
        q2 = create_question("Text2", -5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [q1, q2]
        )

    def test_unpublished_questions(self):
        """ Questions with future pub_dates are not considered published, show No polls message """
        create_question("Future",1)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_published_and_unpublished_questions(self):
        """ Questions with future pub_dates are not considered published, dont' show """
        q1 = create_question("Now", 0)
        q2 = create_question("Future",1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [q1]
        )
