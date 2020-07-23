from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


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
        10 seconds)

        Parameters
        ----------

        elem_id: str
            id of the element to be found
        """
        wait = WebDriverWait(self.driver, 10)

        return wait.until(ec.visibility_of(
            self.driver.find_element_by_id(elem_id)))

    def click_element_by_id(self, elem_id):
        """
        Click of the given element id

        Parameters
        ----------

        elem_id: str
            id of the element to be found
        """
        element = self.driver.find_element_by_id(elem_id)

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
