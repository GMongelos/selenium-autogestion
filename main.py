from src.config import Config
from src.program import Program

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


if __name__ == '__main__':
    conf = Config()
    service_obj = Service(ChromeDriverManager().install())
    p = Program(service_obj, conf)
    p.run()
