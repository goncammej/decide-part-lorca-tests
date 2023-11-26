from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.models import Auth
from census.models import Census
from decide import settings
from voting.models import Question, QuestionOption, Voting
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class MultipleQuestionTestCase(StaticLiveServerTestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        q1 = Question(desc='test question 1')
        q1.save()
        for i in range(3):
            opt = QuestionOption(question=q1, number=i+1, option='option {}'.format(i+1))
            opt.save()

        q2 = Question(desc='test question 2')
        q2.save()
        for i in range(3):
            opt = QuestionOption(question=q2, number=i+1, option='option {}'.format(i+1))
            opt.save()

        q3 = Question(desc='test question 3')
        q3.save()
        for i in range(3):
            opt = QuestionOption(question=q3, number=i+1,option='option {}'.format(i+1))
            opt.save()

        v = Voting(name='test voting 1')
        v.save()
        v.questions.set([q1,q2,q3])

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        u = User(username="testvoter")
        u.set_password("qwerty")
        u.save()

        c = Census.objects.create(voting_id=v.id, voter_id=u.id)
        c.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

    def test_blank_vote(self):
        v = Voting.objects.get(name='test voting 1')
        self.driver.get(f'{self.live_server_url}/booth/{v.id}/')
        self.driver.set_window_size(1888, 994)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()

        goto_logging = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "goto-logging-button"))
            )
        goto_logging.click()

        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
            )
        username.click()

        self.driver.find_element(By.ID, "username").send_keys("testvoter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        self.driver.find_element(By.ID, "process-login-button").click()

        send_vote = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "send-vote"))
            )
        send_vote.click()

        alert_element = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert"))
            )

        assert alert_element is not None and alert_element.get_attribute("variant") == "danger"

        self.driver.close()

    def test_incomplete_vote(self):
        v = Voting.objects.get(name='test voting 1')
        self.driver.get(f'{self.live_server_url}/booth/{v.id}/')
        self.driver.set_window_size(1888, 994)

        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()

        goto_logging = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "goto-logging-button"))
            )
        goto_logging.click()

        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
            )
        username.click()
      
        self.driver.find_element(By.ID, "username").send_keys("testvoter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        self.driver.find_element(By.ID, "process-login-button").click()

        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.ID, "vote"))
            )

        self.driver.find_element(By.ID, "opt1_index0").click()
        self.driver.find_element(By.ID, "opt2_index2").click()

        self.driver.find_element(By.ID, "send-vote").click()

        alert_element = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert"))
            )

        assert alert_element is not None and alert_element.get_attribute("variant") == "danger"

        self.driver.close()

    def test_correct_number_of_questions(self):
        v = Voting.objects.get(name='test voting 1')
        self.driver.get(f'{self.live_server_url}/booth/{v.id}/')
        self.driver.set_window_size(1888, 994)

        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()

        goto_logging = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "goto-logging-button"))
            )
        goto_logging.click()

        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
            )
        username.click()
      
        self.driver.find_element(By.ID, "username").send_keys("testvoter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        self.driver.find_element(By.ID, "process-login-button").click()

        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.ID, "vote"))
            )

        questions = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#vote .form-group'))
        )

        expected_count = v.questions.count()
        actual_count = len(questions)
        assert actual_count == expected_count

        self.driver.close()
