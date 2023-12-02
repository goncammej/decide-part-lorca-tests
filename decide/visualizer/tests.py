from base.tests import BaseTestCase
from census.models import Census
from voting.models import Question, Voting, QuestionOption
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from mixnet.models import Auth
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.conf import settings
from base import mods
import time
from voting.tests import VotingTestCase

class VisualizerTestCase(StaticLiveServerTestCase):
    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v
    
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
            
    def tearDown(self):           
        super().tearDown()
        
        self.driver.quit()
        self.base.tearDown()
            
    def test_visualizer_not_started(self):        
        voting = self.create_voting()
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        voting_state= self.driver.find_element(By.TAG_NAME,"h2").text
        
        self.assertEqual(voting_state, "Voting not started")
    
    def test_visualizer_started_no_census(self):        
        question = Question(desc='test question')
        question.save()
        voting = Voting(name='test voting', start_date=timezone.now(), question_id=question.id)
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        self.assertEqual(self.driver.find_element(By.ID, "participation").text, "-")

    def test_visualizer_started_no_noted(self):        
        question = Question(desc='test question')
        question.save()
        voting = Voting(name='test voting', start_date=timezone.now(), question_id=question.id)
        voting.save()

        census1 = Census(voter_id=1, voting_id=voting.id)
        census1.save()
        census2 = Census(voter_id=2, voting_id=voting.id)
        census2.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        self.assertEqual(self.driver.find_element(By.ID, "participation").text, "0.0%")

    def test_visualizer_census_change(self):        
        question = Question(desc='test question')
        question.save()
        voting = Voting(name='test voting', start_date=timezone.now(), question_id=question.id)
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')

        census_before = self.driver.find_element(By.ID, "census").text

        census1 = Census(voter_id=1, voting_id=voting.id)
        census1.save()
        census2 = Census(voter_id=2, voting_id=voting.id)
        census2.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        census_after = self.driver.find_element(By.ID, "census").text

        self.assertNotEqual(census_before, census_after)
