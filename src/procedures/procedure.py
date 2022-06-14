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

    @abc.abstractmethod
    def ejecutar_procedimiento(self, *args, **kwargs):
        """Ejecuta el procedimiento en base a los parametros ingresados por el usuario,
        toda la lógica va en este método"""
        pass

    @staticmethod
    def abort(msg: str = None):
        """Termina el procedimiento, usar si se encuentra un error"""
        if not msg:
            msg = "PROCEDIMIENTO ABORTADO, REVISE EL LOG PARA MAS INFORMACION"
        raise SystemExit(msg)

    def login(self, driver: webdriver, usr, pswd):
        """Loguea a con las credenciales otorgadas"""

        driver.get(self.config_data.get_url())

        prompt_usuario = driver.find_element(By.NAME, 'ef_form_5000221_datosusuario')
        prompt_usuario.send_keys(usr)

        prompt_pass = driver.find_element(By.NAME, 'ef_form_5000221_datosclave')
        prompt_pass.send_keys(pswd)

        button_login = driver.find_element(By.NAME, 'form_5000221_datos_ingresar')
        button_login.send_keys(Keys.ENTER)

        wrapper.focus_window(driver)

    def inicializar(self, logger: Logger, driver: webdriver):
        """Loguea con credenciales y deja la operación seleccionada"""

        logger.loguear_info(f'Ingresando a con usuario {self.config_data.get_username()}')

        # Loguea con credenciales
        self.login(driver, self.config_data.get_username(), self.config_data.get_password())

        logger.loguear_info('Login finalizado')
        logger.loguear_info(f'COMENZANDO PROCEDIMIENTO {self.TITULO_CONSOLA}')

        # Entrar al menu
        access_menu = driver.find_element(By.ID, 'menu_img')
        access_menu.click()

        # Ingresa nombre de operacion y la clickea
        op_prompt = driver.find_element(By.ID, 'buscar_text')
        op_prompt.send_keys(self.NOMBRE_OPERACION)
        driver.find_element(By.ID, self.ID_HTML).click()
