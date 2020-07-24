"""
MIT License

Copyright (c) 2020 André Lousa Marques <andre.lousa.marques at gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pytest
from pytest_cov.embed import cleanup_on_sigterm
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from worky import server
from worky.storage import Storage
from multiprocessing import Process
from worky.models.index_model import IndexModel
from worky.models.create_task_model import CreateTaskModel
from worky.models.update_task_model import UpdateTaskModel
from worky.models.confirm_form_model import ConfirmFormModel
from worky.models.completed_model import CompletedModel
from tests.utils import date_utils
from tests.utils.e2e_utils import E2eUtils
import os

host_ip = os.getenv("SERVER_IP", "127.0.0.1")

server_url = "http://%s:5000" % host_ip

test_task_description = "Sample task"

UPDATE_BUTTON = 0
DELETE_BUTTON = 1
COMPLETE_BUTTON = 2

DESCRIPTION_COLUMN = 0
DUE_DATE_COLUMN = 1

red_rgba = "rgba(255, 0, 0, 1)"


@pytest.fixture
def deploy_server(tmpdir):
    db_path = str(tmpdir.join("test.worky"))

    server.app.config['STORAGE'] = Storage(db_path)
    server_process = Process(target=server.app.run,
                             args=(host_ip,))

    cleanup_on_sigterm()

    server_process.start()

    yield

    server_process.terminate()
    server_process.join()


@pytest.fixture
def driver_init(request):

    if os.getenv("REMOTE_SELENIUM") is None:
        chrome_driver = webdriver.Chrome()
    else:
        chrome_driver = webdriver.Remote(
            command_executor='http://%s:4444/wd/hub' %
            (os.getenv("REMOTE_SELENIUM")),
            desired_capabilities=DesiredCapabilities.CHROME)

    request.cls.driver = chrome_driver
    request.cls.e2e_utils = E2eUtils(chrome_driver)

    yield

    chrome_driver.close()


@pytest.mark.usefixtures("deploy_server", "driver_init")
class Tests():

    def test_first_open(self):
        self.driver.get(server_url)

        with pytest.raises(NoSuchElementException) as error:
            self.driver.find_element_by_id(IndexModel.task_table_id)

        assert error.type is NoSuchElementException

    def test_create_task(self):
        self.driver.get(server_url)

        self.e2e_utils.click_element_by_id(IndexModel.create_task_button_id)

        due_date = self.e2e_utils.wait_and_get_element_by_id(
            CreateTaskModel.due_date_input_id)

        assert due_date.get_property("value") == date_utils.date_from_today(14)

        desc_area_id = CreateTaskModel.description_area_id,

        self.e2e_utils.send_keys_to_element_by_id(desc_area_id,
                                                  test_task_description)

        self.e2e_utils.click_element_by_id(CreateTaskModel.submit_button_id)

        task_table_id = IndexModel.task_table_id

        table = self.e2e_utils.wait_and_get_element_by_id(task_table_id)

        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 2

        first_row_columns = rows[1].find_elements_by_tag_name("td")

        first_row_desc = first_row_columns[DESCRIPTION_COLUMN].text

        assert first_row_desc == test_task_description

    def _click_task_button(self, row_number, button_number):
        table = self.driver.find_element_by_id(IndexModel.task_table_id)

        rows = table.find_elements_by_tag_name("tr")

        rows[row_number].find_elements_by_tag_name("a")[button_number].click()

    def _create_task(self, task_due_date):
        self.e2e_utils.click_element_by_id(IndexModel.create_task_button_id)

        due_date_picker = self.e2e_utils.wait_and_get_element_by_id(
            CreateTaskModel.due_date_input_id)

        due_date_picker.clear()

        due_date_input_id = CreateTaskModel.due_date_input_id

        self.e2e_utils.send_keys_to_element_by_id(due_date_input_id,
                                                  task_due_date)

        description_area_id = CreateTaskModel.description_area_id

        self.e2e_utils.send_keys_to_element_by_id(description_area_id,
                                                  test_task_description)

        self.e2e_utils.click_element_by_id(CreateTaskModel.submit_button_id)

    def test_update_task(self):
        self.driver.get(server_url)

        self._create_task(date_utils.datepicker_date_from_today(20))

        self._click_task_button(1, UPDATE_BUTTON)

        desc_area_id = UpdateTaskModel.description_area_id

        task_desc = self.e2e_utils.wait_and_get_element_by_id(desc_area_id)

        assert task_desc.text == test_task_description

        task_desc.clear()

        updated_description = "Updated description"

        self.e2e_utils.send_keys_to_element_by_id(desc_area_id,
                                                  updated_description)

        due_date_id = UpdateTaskModel.due_date_input_id

        task_due_date = self.e2e_utils.wait_and_get_element_by_id(due_date_id)

        task_due_date.clear()

        cur_date = date_utils.datepicker_current_date()

        self.e2e_utils.send_keys_to_element_by_id(due_date_id,
                                                  cur_date)

        self.e2e_utils.click_element_by_id(UpdateTaskModel.submit_button_id)

        task_table_id = IndexModel.task_table_id

        table = self.e2e_utils.wait_and_get_element_by_id(task_table_id)

        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 2

        first_row_columns = rows[1].find_elements_by_tag_name("td")

        first_row_desc = first_row_columns[DESCRIPTION_COLUMN].text

        assert first_row_desc == updated_description

        first_row_due_date = first_row_columns[DUE_DATE_COLUMN].text

        assert first_row_due_date == date_utils.current_date()

    def _accept_confirm_form(self):
        desc_area_id = UpdateTaskModel.description_area_id

        task_desc = self.e2e_utils.wait_and_get_element_by_id(desc_area_id)

        assert task_desc.text == test_task_description

        self.e2e_utils.click_element_by_id(ConfirmFormModel.submit_button_id)

    def test_delete_task(self):
        self.driver.get(server_url)

        self._create_task(date_utils.datepicker_date_from_today(20))
        self._create_task(date_utils.datepicker_date_from_today(20))

        task_table_id = IndexModel.task_table_id

        table = self.e2e_utils.wait_and_get_element_by_id(task_table_id)

        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 3

        self._click_task_button(1, DELETE_BUTTON)

        self._accept_confirm_form()

        task_table_id = IndexModel.task_table_id

        table = self.e2e_utils.wait_and_get_element_by_id(task_table_id)

        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 2

    def test_complete_task(self):
        self.driver.get(server_url)

        self._create_task(date_utils.datepicker_date_from_today(20))

        task_table_id = IndexModel.task_table_id

        table = self.e2e_utils.wait_and_get_element_by_id(task_table_id)

        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 2

        self._click_task_button(1, COMPLETE_BUTTON)

        self._accept_confirm_form()

        with pytest.raises(NoSuchElementException):
            self.driver.find_element_by_id(IndexModel.task_table_id)

        self.e2e_utils.click_element_by_id(IndexModel.show_completed_button_id)

        task_table_id = CompletedModel.task_table_id

        comp_table = self.e2e_utils.wait_and_get_element_by_id(task_table_id)

        rows = comp_table.find_elements_by_tag_name("tr")

        assert len(rows) == 2

    def test_task_due_date_ordering(self):
        self.driver.get(server_url)

        self._create_task(date_utils.datepicker_date_from_today(30))
        self._create_task(date_utils.datepicker_date_from_today(15))
        self._create_task(date_utils.datepicker_date_from_today(25))
        self._create_task(date_utils.datepicker_date_from_today(20))
        self._create_task(date_utils.datepicker_current_date())
        self._create_task(date_utils.datepicker_date_from_today(-1))

        task_table_id = IndexModel.task_table_id

        table = self.e2e_utils.wait_and_get_element_by_id(task_table_id)

        rows = table.find_elements_by_tag_name("tr")

        assert len(rows) == 7

        first_row_columns = rows[1].find_elements_by_tag_name("td")

        prev_task_due_date = first_row_columns[DUE_DATE_COLUMN]

        bg_color = prev_task_due_date.value_of_css_property("background-color")

        assert bg_color == red_rgba

        for task in rows[2:]:
            row_columns = task.find_elements_by_tag_name("td")

            assert row_columns[DUE_DATE_COLUMN].text > prev_task_due_date.text

            date_col = row_columns[DUE_DATE_COLUMN]

            bg_color = date_col.value_of_css_property("background-color")

            assert bg_color != red_rgba

            prev_task_due_date = row_columns[DUE_DATE_COLUMN]
