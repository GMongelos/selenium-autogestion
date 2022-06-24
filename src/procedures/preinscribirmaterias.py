"""
Procedimiento para inscribir un alumno a materias. Dada una propuesta y una cantidad finita de alumnos, se logea en
autogestion con cada usuario e intenta preinscribirse a materias dado un criterio. Los criterios que definen al
algoritmo de preinscripción son los siguientes:
    1 - Aleatorio completo: No hay patron de preinscripción. Intenta inscribirse a las 3 alternativas en todas las
        materias posibles que aparezcan en el listado del alumno.
    2 - Aleatorio: No hay patron, se puede saltear inscribirse a materias y hasta puede no inscribirse a las 3
        alternativas
    3 - Igualitario: Las 3 alternativas son iguales.
    5 - Primera: Preinscribe solamente en la primer alternativa.

Parametros de ejecucion:
    - Propuesta: Para facilitar y encapsular los grupos de alumnos que va a preinscribir, se le pide la propuesta al
        usuario así busca alumnos de esa propuesta.
    - Cantidad: Cantidad de alumnos a inscribir, se explica solo.
    - Tipo: El criterio del algoritmo de preinscripcion(explicado anteriormente)
    - Threads: Cantidad de threads a utilizar si se decide utilizar threading.
"""

import random
import time

import selenium.common.exceptions as selenium_exceptions

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.procedures.procedure import Procedure
from src.logger import Logger


class preInscribirMaterias(Procedure):

    NOMBRE_OPERACION = 'Preinscribir alumnos a materias e.e'
    TITULO_CONSOLA = 'Preinscribir alumnos a materias masivamente'
    ID_HTML = 'cursada'
    XPATH_OPERACION = '/html/body/div[2]/div/div/div/ul[1]/li[1]'

    def obtener_parametros(self):
        """ Parámetros que definen el algoritmo de la presincripcion """
        params = dict()

        # TODO: Obtener las propuestas de grado y mostrarlas en pantalla, por el momento hardcodeo sistemas
        # params['propuesta'] = input("Elija la propuesta de los alumnos a inscribir: ").upper()
        params['propuesta'] = 9

        params['cantidad'] = int(input("Cantidad de alumnos a inscribir: "))

        # TODO: Por ahora hardcodeo el tipo 1, mostrar en pantalla los demas.
        # params['tipo'] = input("Ingrese el critero para la inscripcion: ")
        params['tipo'] = 1

        # params['threading'] = input("Usar threading?(Y/N): ").upper()
        # if params['threading'] == 'Y':
        #     params['cant_threads'] = input("Cantidad de threads(se recomienda max 5): ")

        return params

    def generar_datos(self):
        """Obtiene los usuarios para preinscribir según los parámetros otorgados"""

        propuesta = self.parametros.get('propuesta')
        cant = self.parametros.get('cantidad')
        sql = f"""  SELECT  mdp_personas.apellido,
                            mdp_personas.nombres,
                            mdp_personas.usuario,
                            mdp_personas.persona,
                            sga_alumnos.alumno,
                            sga_propuestas.codigo,
                            sga_propuestas.nombre AS nombre_propuesta
                    FROM mdp_personas
                    JOIN sga_alumnos
                        ON mdp_personas.persona = sga_alumnos.persona
                    JOIN sga_propuestas
                        ON sga_alumnos.propuesta = sga_propuestas.propuesta
                    WHERE sga_propuestas.propuesta = {propuesta}
                    AND mdp_personas.usuario IS NOT NULL
                    AND mdp_personas.usuario = '42150836'
                    ORDER BY random()
                    LIMIT {cant};"""

        datos = self.db_instance.consultar(sql)
        return datos

    def prepare_proc(self):
        # TODO: Aca se dividirían los datos cuando se implemente threading, lo dejo así por el momento
        self.ejecutar_procedimiento(self.parametros.get('tipo'), self.datos)

    def ejecutar_procedimiento(self, tipo, datos):
        logger = Logger(log_filename=__name__)

        ag_driver = webdriver.Chrome(service=self.service_obj)
        ag_driver.get(self.config_data.get_url())

        logger.loguear_info(f'INICIANDO PROCEDIMIENTO {self.TITULO_CONSOLA}')

        # Por cada usuario, hacer el procedimiento
        for alumno in datos:
            # Loguea con credenciales, y deja la operacion abierta
            usuario = alumno.get('usuario')
            self.inicializar(logger, ag_driver, usuario)

            # Comienza la salsa

            # Contemplo el caso de aquellas personas que tengan multiples propuestas
            # AFNP, porque si
            try:
                ag_driver.find_element(By.ID, 'js-dropdown-toggle-carreras').click()

                propuestas = ag_driver.find_elements(By.CLASS_NAME, 'js-select-carreras').find_elements_by_tag_name('li')
                for propuesta in propuestas:
                    if propuesta.text.lower() == alumno.get('nombre_propuesta').lower():
                        propuesta.click()
            except selenium_exceptions.NoSuchElementException:
                ag_driver.find_element(By.XPATH, self.XPATH_OPERACION).click()
            finally:
                ag_driver.find_element(By.XPATH, self.XPATH_OPERACION).click()

            # Primero leemos las materias disponibles
            # TODO: Si no hardcodeo los sleeps a veces funciona y a veces no, incluso con los EC, ver que está pasando
            try:
                materias = WebDriverWait(ag_driver, 2).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'js-filter-content'))
                )
            except selenium_exceptions.TimeoutException:
                propuesta = alumno.get('nombre_propuesta')
                logger.loguear_warning(f'No hay materias para {usuario} en la propuesta {propuesta}, continuando con el siguiente')

                self.logout(ag_driver)
                continue

            random.shuffle(materias)
            time.sleep(1)

            # TODO: Hacer esto de forma poliamorfica
            # Tipo 1: totalmente aleatorio
            if self.parametros.get('tipo') == 1:
                # Alternativas 1, 2 y 3
                for i in range(3):
                    logger.log_compuesto_iniciar(f'PREINSCRIPCION ALTERNATIVA {i+1}')
                    for materia in materias:
                        materia.click()
                        time.sleep(1)

                        # Lista de horarios de comision
                        WebDriverWait(ag_driver, 3).until(
                            EC.presence_of_element_located((By.ID, 'comision'))
                        ).click()
                        comisiones = ag_driver.find_elements(By.CSS_SELECTOR, '#comision > option:not([enabled])')

                        # Filtro las comisiones a las que no me puedo inscribir por solapamiento de horario
                        comisiones = [comision for comision in comisiones if comision.is_enabled()]

                        # Existe la posibilidad de que no se pueda inscribir a una materia porque el unico horario
                        # que tiene disponible está ocupado por otra
                        if not comisiones:
                            logger.log_compuesto_add(f'No se pudo preinscribir a la materia {materia.text[2:]}')
                            continue
                        time.sleep(1)

                        # Selecciono un horario aleatorio entre los que haya
                        eleccion = random.choice(comisiones)
                        eleccion.click()

                        # Guardo preinscripcion
                        WebDriverWait(ag_driver, 3).until(
                            EC.presence_of_element_located((By.ID, 'btn-inscribir'))
                        )
                        ag_driver.find_element(By.ID, 'btn-inscribir').click()

                        logger.log_compuesto_add(f'[{materia.text[2:]}] horario [{eleccion.text}]')
                        # time.sleep(1)

                    logger.log_compuesto_commit(f'Finalizada preinscripción de la alternativa {i+1}')

            logger.loguear_info(f"Finalizada preinscripción de {usuario}")
            self.logout(ag_driver)

        logger.log_compuesto_iniciar(f"PROCEDIMIENTO FINALIZADO")
        logger.log_compuesto_add(f"Alumnos procesados: {len(datos)}")
        logger.log_compuesto_add(f"Cantidad de preinscripciones exitosas: ")
        logger.log_compuesto_add(f"Cantidad de preinscripciones no realizadas: ")
        logger.log_compuesto_commit()
