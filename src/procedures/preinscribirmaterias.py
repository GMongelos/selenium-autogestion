"""Procedimiento para inscribir un alumno a materias WIP"""

import random
import time

import selenium.common.exceptions

from selenium import webdriver
from selenium.webdriver.common.by import By

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
        # TODO: Aca se dividirían los datos si implementa threading, por ahora lo dejo plano
        self.ejecutar_procedimiento(self.parametros.get('tipo'), self.datos)

    def ejecutar_procedimiento(self, tipo, datos):
        logger = Logger(log_filename=__name__)

        gestion_driver = webdriver.Chrome(service=self.service_obj)
        gestion_driver.get(self.config_data.get_url())

        # Por cada usuario, hacer el procedimiento
        for alumno in datos:
            # Loguea con credenciales, y deja la operacion abierta
            self.inicializar(logger, gestion_driver, alumno.get('usuario'))

            # Logica va aca
            time.sleep(3)