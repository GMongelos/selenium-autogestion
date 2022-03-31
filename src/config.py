"""Clase que engloba la lectura y obtencion de datos del archivo de configuracion"""
import os
from configparser import ConfigParser


class Config:

    def __init__(self, file_path='config.ini'):
        """Lee los datos de config.ini y los guarda en un diccionario"""

        cparser = ConfigParser()
        cparser.read(file_path)

        self.data = dict()
        for section in cparser.sections():
            self.data.update({section: dict(cparser.items(section))})

    # TODO: Parametrizar los gets que quedaron feitos hardcodeados
    def get_username(self):
        return self.data['USERINFO'].get('username')

    def get_password(self):
        return self.data['USERINFO'].get('password')

    def get_url(self):
        return self.data['SERVERCONFIG'].get('url')

    def get_server_info(self):
        return self.data['DATABASECONFIG']
