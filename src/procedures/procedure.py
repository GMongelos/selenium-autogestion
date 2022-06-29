"""
Clase padre de todos los procedures.
La base de un procedure debería ser la siguiente:
1. Obtener parametros: Se le pide al usuario todos los parametros necesarios para la ejecucion. Ej: dni del objetivo
    con el cual se va a operar, si usa threading o no, etc.
2. Generar datos: Genera datos concretos que se utilizan en el procedimiento. Algunos procedures pueden leer datos
    de un archivo csv o excel.
3. Preparar procedure: Con parametros + datos configurar cómo se va a correr el procedure.
4. Ejecutar: En base a los 3 pasos anteriores, ejecutar el procedure. Esto termina y comienza, idealmente, sin
    intervención del usuario.
"""

import abc
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import src.wrapper as wrapper

from src.logger import Logger
from src.pg import GuaraniDB
from src.config import Config


class Procedure:
    # TODO: Ver la forma de verificar que esten los atributos de clase implementados cuando hereda
    NOMBRE_OPERACION = 'NOMBRE_OPERACION NO SETEADO'
    TITULO_CONSOLA = 'TITULO_CONSOLA NO SETEADO'
    ID_HTML = 'ID_HTML NO SETEADO'

    def __init__(self, conf_obj: Config, database: GuaraniDB):
        """Configura la conexion con la base y pide los parametros del procedimiento al usuario"""
        self.config_data = conf_obj
        self.service_obj = Service(ChromeDriverManager().install())
        self.db_instance = database

        self.parametros: dict = self.obtener_parametros()
        self.datos = self.generar_datos()

    @abc.abstractmethod
    def obtener_parametros(self):
        """Pide al usuario todos los parametros necesarios antes de ejecutar el procedimiento"""
        pass

    @abc.abstractmethod
    def generar_datos(self):
        """
        Para generar datos hay dos posibilidades:
        - Leer los datos de un archivo ubicado en el directorio raw_data
        - Generarlos de forma propia a partir de los parametros otorgados
        """
        pass

    @abc.abstractmethod
    def prepare_proc(self):
        """
        Configura el procedimiento con lo parametros que se pasaron y los datos
        leidos(si corresponde). Luego lo ejecuta
        """
        pass

    @staticmethod
    def abort(msg: str = None):
        """Termina el procedimiento, usar si se encuentra un error"""
        if not msg:
            msg = "PROCEDIMIENTO ABORTADO, REVISE EL LOG PARA MAS INFORMACION"
        raise SystemExit(msg)

    @abc.abstractmethod
    def ejecutar_procedimiento(self, *args, **kwargs):
        """Ejecuta el procedimiento en base a los parametros ingresados por el usuario,
        toda la lógica va en este método"""
        pass

    def login(self, driver: webdriver, usr, pswd):
        """Loguea sin credenciales porque en tst debería estar el login mockeado"""

        # Input de usuario y contraseña
        wrapper.wait_for(driver, 'usuario')
        driver.find_element(By.ID, 'usuario').send_keys(usr)
        driver.find_element(By.ID, 'password').send_keys(pswd)

        # Click al boton de login, uso xpath completo porque de otra forma no lo clickea
        driver.find_element(By.XPATH, '/html/body/div[6]/div/div[1]/div/form/div[3]/div/input').click()

    def logout(self, driver: webdriver):
        driver.find_element(By.CLASS_NAME, 'dropdown').click()
        time.sleep(0.5)
        driver.find_element(By.CLASS_NAME, 'icon-off').click()
        time.sleep(0.5)

    def inicializar(self, logger: Logger, driver: webdriver, username):
        """Loguea con credenciales y deja la operación seleccionada"""

        logger.loguear_info(f'Ingresando con usuario {username}')
        # Se puede ingresar cualquier contraseña, "x" es cortito y fachero
        self.login(driver, username, "x")
        logger.loguear_info('Login finalizado')

        # Clickea en la operacion
        wrapper.wait_for(driver, self.ID_HTML)
        # qcyo ya estoy paranoico porque a veces no funciona
        driver.find_element(By.ID, self.ID_HTML).click()
        time.sleep(0.5)
