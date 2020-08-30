from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time


class E2eUtils():
    """
    Utilities for end-to-end testing
    """
    def __init__(self, driver):
        """
        Constructor

        Parameters
        ----------
        driver : selenium.webdriver
            selenium driver instance
        """
        self.driver = driver

    def wait_and_get_element_by_id(self, elem_id):
        """
        wait for the given element id to appear before returning it (wait up to
        30 seconds)

        Parameters
        ----------

        elem_id: str
            id of the element to be found
        """
        wait = WebDriverWait(self.driver, 30)

        return wait.until(ec.visibility_of_element_located((By.ID, elem_id)))

    def wait_and_click_element_by_id(self, elem_id):
        """
        Wait for the given element id to be clickable and click on it (wait up
        to 30 seconds)

        Parameters
        ----------

        elem_id: str
            id of the element to be found
        """
        wait = WebDriverWait(self.driver, 30)

        element = wait.until(ec.element_to_be_clickable((By.ID, elem_id)))

        element.click()

    def wait_and_send_keys_to_element_by_id(self, elem_id, keys):
        """
        Wait for the given element id to be visible before sending keys to it
        (wait up to 30 seconds)

        Parameters
        ----------

        elem_id: str
            id of the element to be found

        keys : str
            the keys to send
        """
        wait = WebDriverWait(self.driver, 30)

        element = wait.until(ec.visibility_of_element_located(
            (By.ID, elem_id)))

        " ensure the element is focused "
        element.clear()

        """
        the webdriver can be slow, so we split the keys into 4-char chunks as
        that is the length of the year field of a datepicker, which needs to
        be writen as a single chunk
        """
        chunks = [keys[i:i+4] for i in range(0, len(keys), 4)]

        for c in chunks:
            " allow time for the webdriver to prepare for the keys "
            time.sleep(1)
            element.send_keys(c)
