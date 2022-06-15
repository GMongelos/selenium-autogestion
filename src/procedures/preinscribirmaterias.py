"""Procedimiento para inscribir un alumno a materias WIP"""

import random
import time

import selenium.common.exceptions

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.procedures.procedure import Procedure
from src.logger import Logger


class preInscribirMaterias(Procedure):

    NOMBRE_OPERACION = 'Preinscribir alumnos a materias e.e'
    TITULO_CONSOLA = 'Preinscribir alumnos a materias masivamente'
    ID_HTML = 'cursada'

    def obtener_parametros(self):
        """
        Parámetros que definen el algoritmo dela presincripcion masiva

        """
        params = dict()

        # TODO: Obtener las propuestas de grado y mostrarlas en pantalla, por el momento hardcodeo sistemas
        # params['propuesta'] = input("Elija la propuesta de los alumnos a inscribir: ").upper()
        params['propuesta'] = 9

        # TODO: Deshadcodear, por ahora pruebo con dos
        # params['cantidad'] = int(input("Cantidad de alumnos a inscribir: "))
        params['cantidad'] = 2

        """
        Criterios, define el algoritmo de preinscripcion:
            1 - Aleatorio: No hay patron, se puede inscribir a todo y todas sus alternativas como no.
            2 - Completo: Preinscribe al alumno en las 3 alternativas, siendo estas 3 distintas(si es posible)
            3 - Igualitario: Las 3 alternativas son iguales para todos
            4 - Igualitario aleatorio: Las 3 alternativas puedens ser iguales, o 2 o 1 :)
            5 - Solo primera: Inscribe a todos solamente en la primer alternativa.
        """
        # TODO: Por ahora hardcodeo el tipo 1, mostrar en pantalla los demas.
        # params['tipo'] = input("Ingrese el critero para la inscripcion: ")
        params['tipo'] = 1

        # params['threading'] = input("Usar threading?(Y/N): ").upper()
        # if params['threading'] == 'Y':
        #     params['cant_threads'] = input("Cantidad de threads(se recomienda max 5): ")

        return params

    def generar_datos(self):
        """Obtiene los usuarios para preinscribir según los parámetros otorgados"""

        # todo: dESHARDCODEAR PAFUNDI
        propuesta = self.parametros.get('propuesta')
        cant = self.parametros.get('cantidad')
        sql = f"""  SELECT  mdp_personas.apellido,
                            mdp_personas.nombres,
                            mdp_personas.usuario,
                            sga_propuestas.codigo,
                            sga_propuestas.nombre
                    FROM mdp_personas
                    JOIN sga_alumnos
                        ON mdp_personas.persona = sga_alumnos.persona
                    JOIN sga_propuestas
                        ON sga_alumnos.propuesta = sga_propuestas.propuesta
                    WHERE sga_propuestas.propuesta = {propuesta}
                    AND mdp_personas.usuario IS NOT NULL
                    AND mdp_personas.usuario = 'mpafundi'
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

        logger.loguear_info(f'COMENZANDO PROCEDIMIENTO {self.TITULO_CONSOLA}')

        # Por cada usuario, hacer el procedimiento
        for alumno in datos:
            # Loguea con credenciales, y deja la operacion abierta
            self.inicializar(logger, ag_driver, alumno.get('usuario'))

            # Comienza la salsa

            # Primero leemos las materias disponibles
            # TODO: Si no hardcodeo los sleeps a veces funciona y a veces no, incluso con los EC, ver que está pasando
            materias = WebDriverWait(ag_driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'js-filter-content'))
            )
            random.shuffle(materias)

            # Alternativas 1, 2 y 3
            for i in range(3):
                for materia in materias:
                    materia.click()
                    time.sleep(1)

                    # Lista de horarios de comision
                    WebDriverWait(ag_driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'comision'))
                    ).click()
                    comisiones_select = Select(ag_driver.find_element(By.ID, 'comision'))

                    # Selecciono un horario aleatorio entre los que haya
                    indice = random.randrange(1, len(comisiones_select.options))
                    comisiones_select.select_by_index(indice)

                    aux = comisiones_select.first_selected_option
                    time.sleep(1)

                    # Guardo preinscripcion
                    WebDriverWait(ag_driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'btn-inscribir'))
                    )
                    ag_driver.find_element(By.ID, 'btn-inscribir').click()
                    time.sleep(1)
                logger.loguear_info(f'Finalizada preinscripción de la alternativa {i+1}')