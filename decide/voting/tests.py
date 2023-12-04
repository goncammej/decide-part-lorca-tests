import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, tag
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption, QuestionOptionRanked
from datetime import datetime


class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

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
    
    def create_ranked_voting(self):
        q = Question(desc='ranked test question', type='R')
        q.save()
        for i in range(5):
            opt = QuestionOptionRanked(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test ranked voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    @tag("slow")
    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_complete_ranked_voting(self):
        v = self.create_ranked_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()
        # v.tally_votes(self.token)

        # tally = v.tally
        # tally.sort()
        # tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        # for q in v.question.options.all():
        #     self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        # for q in v.postproc:
        #     self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_voting_from_api_ranked(self):
        data = {'name': 'Voting ranked'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Voting ranked',
            'desc': 'Description example',
            'question': {
                'desc': 'Choose your prefered option',
                'type': 'R'
            },
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        #self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')

class LogInSuccessTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def successLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/")

class LogInErrorTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def usernameWrongLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

    def passwordWrongLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("wrongPassword")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

class QuestionTestCases(BaseTestCase):

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        super().tearDown()

    def test_question_to_string(self):
        q = Question(desc='test question', type='C')
        self.assertEqual(str(q), 'test question')

    def test_question_option_to_string(self):
        q = Question(desc='test question', type='C')
        opt = QuestionOption(number=1, option='test option', question=q)
        self.assertEqual(str(opt), 'test option (1)')

    def test_question_option_ranked_to_string(self):
        q = Question(desc='test question', type='R')
        opt = QuestionOptionRanked(number=1, option='test option', question=q)
        self.assertEqual(str(opt), 'test option (1)')

    def test_question_option_ranked_error_str(self):
        q = Question(desc='test question', type='C')
        opt = QuestionOptionRanked(number=1, option='test option', question=q)
        self.assertEqual(str(opt), 
                         'You cannot create a ranked option for a non-ranked question')

    def test_question_option_error_str(self):
        q = Question(desc='test question', type='R')
        opt = QuestionOption(number=1, option='test option', question=q)
        self.assertEqual(str(opt), 
                         'You cannot create a classic option for a non-classical question')

    def test_question(self):
        q1 = Question(desc='test question', type='C')
        q1.save()
        q2 = Question(desc='test question', type='R')
        q2.save()

        self.assertEqual(q1.type, 'C')
        self.assertEqual(q2.type, 'R')
        self.assertEqual(q1.desc, 'test question')
        self.assertEqual(q2.desc, 'test question')

    def test_question_option(self):
        Question(desc='test question', type='C').save()
        q = Question.objects.get(desc='test question')
        QuestionOption(number=1, option='test option', question=q).save()
        opt = QuestionOption.objects.get(option='test option')

        self.assertEqual(opt.number, 1)
        self.assertEqual(opt.option, 'test option')
        self.assertEqual(opt.question, q)

    def test_question_option_error(self):
        Question(desc='test question', type='R').save()
        q = Question.objects.get(desc='test question')
        QuestionOption(number=1, option='test option', question=q).save()
        self.assertRaises(QuestionOption.DoesNotExist)

    def test_question_option_ranked(self):
        Question(desc='test question', type='R').save()
        q = Question.objects.get(desc='test question')
        QuestionOptionRanked(number=1, option='test option', question=q).save()
        opt = QuestionOptionRanked.objects.get(option='test option')

        self.assertEqual(opt.number, 1)
        self.assertEqual(opt.option, 'test option')
        self.assertEqual(opt.question, q)

    def test_question_option_ranked_error(self):
        Question(desc='test question', type='C').save()
        q = Question.objects.get(desc='test question')
        QuestionOptionRanked(number=1, option='test option', question=q).save()
        self.assertRaises(QuestionOptionRanked.DoesNotExist)
    
# class PostProcTest(TestCase):
#     def setUp(self):
#         super().setUp()

#     def tearDown(self):
#         super().tearDown()
    
#     def test_do_postproc(self):
#         q = Question(desc='test question', type='R')
#         q.save()
#         op1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
#         op2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
#         op1.save()
#         op2.save()
#         v = Voting(name='test voting', question=q)
#         v.save()
#         a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
#                                           defaults={'me': True, 'name': 'test auth'})
#         a.save()
#         v.auths.add(a)

#         tally = {
#             'msgs': ['1-2', '2-1']
#         }
#         v.tally = tally
#         v.save()

#         v.do_postproc()

#         self.assertEqual(v.postproc[0]['votes'], 3)
#         self.assertEqual(v.postproc[1]['votes'], 3)
#         self.assertEqual(v.postproc[0]['postproc'], 3)
#         self.assertEqual(v.postproc[1]['postproc'], 3)

#     def test_do_postproc_no_votes(self):
#         q = Question(desc='test question', type='R')
#         q.save()
#         op1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
#         op2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
#         op1.save()
#         op2.save()
#         v = Voting(name='test voting', question=q)
#         v.save()
#         a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
#                                           defaults={'me': True, 'name': 'test auth'})
#         a.save()
#         v.auths.add(a)

#         # Simulate a tally with no votes
#         tally = {}

#         v.tally = tally
#         v.save()

#         v.do_postproc() 

#         self.assertEqual(v.postproc[0]['votes'], 0)
#         self.assertEqual(v.postproc[1]['votes'], 0)
#         self.assertEqual(v.postproc[0]['postproc'], 0)
#         self.assertEqual(v.postproc[1]['postproc'], 0)

#     def test_do_postproc_invalid_vote(self):
#         q = Question(desc='test question', type='R')
#         q.save()
#         op1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
#         op2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
#         op1.save()
#         op2.save()
#         v = Voting(name='test voting', question=q)
#         v.save()
#         a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
#                                           defaults={'me': True, 'name': 'test auth'})
#         a.save()
#         v.auths.add(a)

#         tally = {
#             'msgs': ['1-2', '2-x']
#         }
#         v.tally = tally
#         v.save()

#         with self.assertRaises(ValueError):
#             v.do_postproc()