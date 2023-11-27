from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django.utils import timezone

from base.tests import BaseTestCase
from voting.models import Question, Voting, QuestionOption
import time
from census.models import Census
from mixnet.models import Auth
from django.conf import settings
from django.contrib.auth.models import User


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class MultipleChoiceQuestionBoothTest(StaticLiveServerTestCase):

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
    
    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user
    
    def setUp(self):
        #Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
	
        self.v = self.create_voting()
        self.v.question.type = 'M'
        self.v.question.save()

        #Añadimos al usuario noadmin al censo y empezamos la votacion
        user = self.get_or_create_user(1)
        user.is_active = True
        user.save()
        c = Census(voter_id=user.id, voting_id=self.v.id)
        c.save()

        self.v.create_pubkey()
        self.v.start_date = timezone.now()
        self.v.save()
    
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_testquestionmultipleoptions(self):
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "username").send_keys("noadmin")
        time.sleep(1)

        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(1) > .form-check").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(2) > .form-check").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .form-check").click()
        
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, '.form-check input[type="checkbox"]')

        selected_checkboxes = [checkbox for checkbox in checkboxes if checkbox.is_selected()]


        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        self.assertTrue(len(selected_checkboxes)==3)
        self.assertTrue(len(self.driver.find_elements(By.CSS_SELECTOR, 'form'))==5)
    
