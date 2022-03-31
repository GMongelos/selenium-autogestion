"""Lógica del programa o qcyo"""
import sys

import src.wrapper as wrapper

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.pg import GuaraniDB
from src.config import Config
from src.vista import consola

from src.procedures import Procedure
import inspect


class Program:

    def __init__(self, service_obj, conf_obj: Config):
        """Instancia la conexion a la base de datos y el objeto webdriver"""

        self.db = GuaraniDB(conf_obj.get_server_info())
        self.config_data = conf_obj
        self.ag_driver = webdriver.Chrome(service=service_obj)
        self.menu = dict()

        # Leo la lista de funciones de Procedures y luego las guardo en un dict.
        self.listaFunciones = inspect.getmembers(Procedure, predicate=inspect.isfunction)

        for i in range(0, len(self.listaFunciones)):
            self.menu[f"{i + 1}"] = f"{self.listaFunciones[i][0]}"

    def run(self):
        """Abre el navegador con la url especificada en config, loguea con credenciales y espera input de usuario"""
        #TODO Que queres hacer? Probar algo con tu usuario? o hacer algo con otro usuario?


    def salir_aplicacion(self, msg=''):
        if msg:
            print(msg)

        self.db.terminar_conexion()
        self.ag_driver.close()
        self.ag_driver.quit()
        sys.exit()
