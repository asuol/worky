from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


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

    def send_keys_to_element_by_id(self, elem_id, keys):
        """
        Send keys to the given element id

        Parameters
        ----------

        elem_id: str
            id of the element to be found

        keys : str
            the keys to send
        """

        element = self.driver.find_element_by_id(elem_id)

        element.send_keys(keys)
