from django.test import TestCase
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django.utils import timezone

from base.tests import BaseTestCase
import time
from census.models import Census
from voting.models import Question, Voting, Auth, QuestionOptionRanked
from django.contrib.auth.models import User


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

class AdminTestCase(StaticLiveServerTestCase):

    def create_voting(self):
        q = Question(desc='test question', type='R')
        q.save()
        opt1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
        opt2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
        opt1.save()
        opt2.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def get_or_create_user(self,pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = f'user: {pk}'
        user.set_password('qwerty')
        user.save()
        return user

    def setUp(self):
        #Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()

        v = self.create_voting()
        v.question.type = 'R'
        v.question.save()
        self.v = v
        #Añadimos al usuario noadmin al censo y empezamos la votacion
        user = self.get_or_create_user(1)
        user.is_active = True
        user.save()
        c = Census(voter_id=user.id, voting_id=v.id)
        c.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
    
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_question_preference(self):
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

        # Realizar la votación votando Sí
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").send_keys("2")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Verificar que la votación se realizó correctamente
        success_alert = self.driver.page_source
        expected_text = "Congratulations. Your vote has been sent"
        self.assertTrue(expected_text in success_alert, "La alerta de éxito no está presente después de votar")
    
    def test_preference_booth_same_preference(self):
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

        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Verificar que la votación se realizó correctamente
        canceled_alert = self.driver.page_source
        expected_text = "Error: No puede haber preferencias repetidas entre opciones"
        self.assertTrue(expected_text in canceled_alert, "La alerta de éxito no está presente después de votar")

    def test_preference_booth_no_fullfile_all_preferences(self):
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

        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Verificar que la votación se realizó correctamente
        canceled_alert = self.driver.page_source
        expected_text = "Error: Se tienen que escoger la preferencia de todas las opciones"
        self.assertTrue(expected_text in canceled_alert, "La alerta de éxito no está presente después de votar")
