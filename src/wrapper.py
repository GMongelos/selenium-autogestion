"""Modulo que envuelve varias funcionalidades necesarias para las ejecuciones de las operaciones"""

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


def focus_window(driver: webdriver):
    """Hace cosas con las ventanas, sirve solo para """

    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]

    # Switch al popup -> gracias siu por ser tan inconveniente
    driver.switch_to.window(window_after)
    driver.close()

    # Vuelvo al mi ventana original y recargo
    driver.switch_to.window(window_before)
    driver.refresh()


def wait_for(driver: webdriver, element_id):
    """Espera a que un elemento en particular esté en pantalla"""

    return WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.ID, str(element_id))))


# TODO: Decidir qué hacer con esto
class WebElementWrapper:
    def __init__(self):
        pass

    def click_on(self, id_element):
        """Clickea en un elemento dado su id"""

        pass


