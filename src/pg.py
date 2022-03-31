"""Módulo de conexión con la base de datos"""

import psycopg2
from psycopg2 import Error


def instance_cursor(config_user, config_password, config_host, config_database):
    """Instancia una conexión y retorna el cusor"""
    conn = psycopg2.connect(user=config_user, password=config_password, host=config_host, database=config_database)
    curr = conn.cursor()
    curr.execute("set search_path = 'negocio';")
    return curr, conn


# Singleton - Copiado y pegado, no preguntes
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GuaraniDB(metaclass=Singleton):
    """DAO para acceder a la base de datos"""

    __cursor = None

    # TODO: eliminar verificacion
    def __init__(self, server_info: dict):
        self.__cursor, self.__conn = instance_cursor(config_user=server_info.get('username'),
                                                     config_password=server_info.get('password'),
                                                     config_host=server_info.get('host'),
                                                     config_database=server_info.get('dbname'))

    def get_cursor(self):
        return self.__cursor

    def consultar(self, sql: str, asoc=True):
        """Consulta en la base haciendo un fetchall
        Parameters:
            sql (str):      query sql para consultar
            asoc (bool):    indica si retorna la consulta como un diccionario
        """
        self.get_cursor().execute(sql)
        fetch = self.get_cursor().fetchall()
        resultado = [self.tuple_to_dict(row) for row in fetch] if asoc else fetch
        return resultado

    def ejecutar(self, sql):
        """Ejecuta una query y no hace ningún fetch"""

        print(f'Ejecutando sql: {sql}')
        curr = self.get_cursor()
        try:
            # a = 1
            curr.execute(sql)
            # self.__conn.commit()
        except psycopg2.DatabaseError as ejecutar_error:
            print(ejecutar_error)
            self.__conn.rollback()
            raise Exception

    def commit(self):
        print(f'Commiteando sql')
        try:
            self.__conn.commit()
        except psycopg2.DatabaseError as commit_error:
            print(commit_error)
            self.__conn.rollback()

    def consultar_fila(self, sql, asoc=True):
        """Consulta en la base y retorna el primer registro
        Parameters:
            sql (str):      query sql para consultar
            asoc (bool):    indica si retorna la consulta como un diccionario
        """
        print(f'consulta sql: {sql}')
        self.get_cursor().execute(sql)
        fetch = self.get_cursor().fetchone()
        resultado = [self.tuple_to_dict(row) for row in fetch] if asoc else fetch
        return resultado

    def tuple_to_dict(self, row):
        """Transforma una row de una consulta en un diccionario usando los headers"""
        columns = [x.name for x in self.get_cursor().description]
        return {columns[index]: value for index, value in enumerate(row)}

    def terminar_conexion(self):
        self.__cursor.close()
        self.__conn.close()
        print("Conexion finalizada")
