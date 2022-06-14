"""Procedimiento para inscribir un alumno a materias WIP"""

import random
import time

import selenium.common.exceptions

from selenium import webdriver
from selenium.webdriver.common.by import By

from src.procedures.procedure import Procedure
from src.logger import Logger


class preInscribirMaterias(Procedure):

    NOMBRE_OPERACION = 'Administrar Docentes'
    TITULO_CONSOLA = 'Dar de alta docentes'
    ID_HTML = 'elemento_buscar_menu_45000002'

    def obtener_parametros(self):
        """
        Pregunta el dni de la persona para dar de alta como docente
        """
        params = dict()
        params['dni'] = input("Ingrese el documento de la persona para dar de alta: ").upper()
        return params

    def generar_datos(self):
        """Genera el legajo del nuevo docente, pregunta en la bd si ya existe, si existe crea otro"""

        # No está contemplado el super hipotetico caso de genere infinitos legajos que ya existan
        legajo = str(random.randint(1000000000, 9999999999))
        sql = f"""SELECT EXISTS(SELECT * FROM sga_docentes WHERE legajo = '{legajo}');"""
        existe = self.db_instance.consultar_fila(sql, False)
        if existe:
            self.generar_datos()
        else:
            return legajo

    def prepare_proc(self):
        # No hay que preparar nada ya que es un procedimiento relativamente simple
        self.ejecutar_procedimiento(self.parametros.get('dni'), self.datos)

    def ejecutar_procedimiento(self, dni, legajo):
        logger = Logger(log_filename=self.__module__)

        gestion_driver = webdriver.Chrome(service=self.service_obj)
        gestion_driver.get(self.config_data.get_url())

        # Loguea con credenciales, y deja la operacion abierta
        self.inicializar(logger, gestion_driver)

        # Lógica propia del procedure
        gestion_driver.find_element(By.ID, 'ci_45000011_agregar').click()

        # Añadir persona para agregarle rol docente
        gestion_driver.find_element(By.ID, 'ef_form_38000698_form_datos_docentepersona_vinculo').click()

        window_before = gestion_driver.window_handles[0]
        window_after = gestion_driver.window_handles[1]

        logger.loguear_info(f'Buscando persona con dni {dni}')

        # Switch al popup
        gestion_driver.switch_to.window(window_after)
        gestion_driver.find_element(By.ID, 'ef_ei_37000921_filtronro_documento').send_keys(dni)
        gestion_driver.find_element(By.ID, 'ei_37000921_filtro_filtrar').click()

        # Me fijo si existe la persona con el dni provisto
        try:
            nombre = gestion_driver.find_element(
                By.XPATH,
                '//*[@id="cuerpo_js_cuadro_39000087_cuadro"]/tbody/tr[2]/td/table/tbody/tr[2]/td[1]').text
            gestion_driver.find_element(By.ID, 'cuadro_39000087_cuadro0_seleccion').click()
        except selenium.common.exceptions.NoSuchElementException:
            logger.loguear_exepcion('No se pudo agregar el docente')
            self.abort()

        logger.loguear_info(f'SELECCIONADO {nombre}')

        # Vuelvo a la pestaña principal
        gestion_driver.switch_to.window(window_before)

        # Ingreso el legajo generado
        logger.loguear_info(f'Usando legajo {legajo}')
        gestion_driver.find_element(By.ID, 'ef_form_38000698_form_datos_docentelegajo').send_keys(legajo)

        # Selecciono todos los roles y responsables academicas
        gestion_driver.find_element(By.LINK_TEXT, 'Todos').click()
        gestion_driver.find_element(
            By.XPATH,
            '/html/body/div[6]/form/table/tbody/tr/td/div[3]/div[1]/div/table/tbody/tr/td/div[2]/div/div/table[3]/tbody/tr/td/div[3]/div/div/div[1]/a[1]').click()
        gestion_driver.find_element(By.ID, 'ci_45000011_guardar').click()

        # Si gestion me da un error, informo al usuario
        time.sleep(5)
        error: str = gestion_driver.find_element(By.CLASS_NAME, 'overlay-mensaje').text
        if error:
            logger.loguear_error(error[:error.find('.')])
            self.abort()
        else:
            logger.loguear_info(f'Docente {nombre} añadido con exito')
