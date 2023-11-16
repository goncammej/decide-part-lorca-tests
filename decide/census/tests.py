import random
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from openpyxl import load_workbook
from io import BytesIO
from openpyxl import Workbook
from django.core.files.uploadedfile import SimpleUploadedFile

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .models import Census
from voting.models import Voting, Question, QuestionOption
from base.models import Auth
from base import mods
from base.tests import BaseTestCase
from datetime import datetime


class CensusTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get(
            "/census/{}/?voter_id={}".format(1, 2), format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), "Invalid voter")

        response = self.client.get(
            "/census/{}/?voter_id={}".format(1, 1), format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Valid voter")

    def test_list_voting(self):
        response = self.client.get("/census/?voting_id={}".format(1), format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.get("/census/?voting_id={}".format(1), format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get("/census/?voting_id={}".format(1), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"voters": [1]})

    def test_add_new_voters_conflict(self):
        data = {"voting_id": 1, "voters": [1]}
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {"voting_id": 2, "voters": [1, 2, 3, 4]}
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 401)

        self.login(user="noadmin")
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get("voters")), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {"voters": [1]}
        response = self.client.delete("/census/{}/".format(1), data, format="json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())


class CensusTest(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
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

    def createCensusSuccess(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys(
            now.strftime("%m%d%M%S")
        )
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys(
            now.strftime("%m%d%M%S")
        )
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.current_url == self.live_server_url + "/admin/census/census"
        )

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/census/census/add"
        )

    def createCensusValueError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys("64654654654654")
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys("64654654654654")
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/census/census/add"
        )


class CensusExportViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def create_voting(self):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def test_census_export_view(self):
        self.create_voting()

        url = reverse("export_census")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue("votings" in response.context)

        votings = response.context["votings"]
        self.assertEqual(votings.count(), Voting.objects.count())

        self.assertTemplateUsed(response, "census/export_census.html")


class ExportCensusTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def create_voting(self):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username="testvoter{}".format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def test_export_census(self):
        v = self.create_voting()
        self.create_voters(v)

        url = reverse("export_census_of_voting", args=[v.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.assertEqual(
            response["Content-Disposition"], "attachment; filename=census.xlsx"
        )

        workbook = load_workbook(BytesIO(response.content))
        worksheet = workbook.active

        self.assertEqual(worksheet["A1"].value, f"Census for: {v.name}")

        self.assertEqual(worksheet["A2"].value, "Voting ID")
        self.assertEqual(worksheet["B2"].value, "Voter ID")

        census_data = Census.objects.filter(voting_id=v.id)
        for i, row in enumerate(census_data, start=3):
            self.assertEqual(worksheet[f"A{i}"].value, row.voting_id)
            self.assertEqual(worksheet[f"B{i}"].value, row.voter_id)


class CensusImportViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def create_voting(self):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def test_census_import_view_success(self):
        self.create_voting()

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Voting ID", "Voter ID"])
        sheet.append([1, 1])
        sheet.append([1, 2])

        file_buffer = BytesIO()
        workbook.save(file_buffer)
        file_buffer.seek(0)

        excel_file = SimpleUploadedFile("census.xlsx", file_buffer.read())

        url = reverse("import_census")

        response = self.client.post(url, {"file": excel_file}, follow=True)

        self.assertEqual(response.status_code, 200)

        census_data = Census.objects.all()
        self.assertEqual(census_data.count(), 2)
        self.assertEqual(census_data[0].voting_id, 1)
        self.assertEqual(census_data[0].voter_id, 1)
        self.assertEqual(census_data[1].voting_id, 1)
        self.assertEqual(census_data[1].voter_id, 2)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Data imported successfully!")

    def test_census_import_view_fail(self):
        self.create_voting()

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Voting ID", "Voter ID"])
        sheet.append(["A", "B"])

        file_buffer = BytesIO()
        workbook.save(file_buffer)
        file_buffer.seek(0)

        excel_file = SimpleUploadedFile("census.xlsx", file_buffer.read())

        url = reverse("import_census")

        response = self.client.post(url, {"file": excel_file}, follow=True)

        self.assertEqual(response.status_code, 200)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertTrue("Error importing data" in str(messages[0]))

    def test_census_import_view_no_file(self):
        url = reverse("import_census")

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No file selected!")
