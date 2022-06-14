"""Lógica del programa o qcyo"""
import sys

from src import procedures
from src.pg import GuaraniDB
from src.config import Config
from src.vista import consola
import inspect


class Program:

    def __init__(self, conf_obj: Config):
        """
        Instancia la conexion a la base de datos,
        luego guardo la instancia de configuraicon y leo los procedures
        """
        self.config_data = conf_obj
        self.db = GuaraniDB(conf_obj.get_server_info())
        self.menu = dict()

    def run(self):
        """Renderiza el menu en pantalla y espera input de usuario. Luego ejecuta el procedimiento seleccionado"""

        opcion = consola.renderizar_menu(procedures.procs)
        if opcion != '0':
            # Instancio el procedure y lo corro
            p = procedures.procs.get(opcion)[1](self.config_data, self.db)
            p.prepare_proc()

            self.salir_aplicacion("Proceso terminado con exito, revise los logs para mas informacion")
        else:
            self.salir_aplicacion("Saliendo del programa..")

    def salir_aplicacion(self, msg=''):
        if msg:
            print(msg)

        self.db.terminar_conexion()
        sys.exit()
