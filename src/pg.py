"""Módulo de conexión con la base de datos"""

import psycopg2
import psycopg2.extras


def instance_cursor(config_user, config_password, config_host, config_database):
    """Instancia una conexión y retorna los cursores normal y el asociativo"""
    try:
        print("Conectando a la base de datos...")
        conn = psycopg2.connect(user=config_user, password=config_password, host=config_host, database=config_database)
    except psycopg2.DatabaseError:
        msg = "Error al conectar con la base de datos, " \
              "verifique su conexion a internet, el archivo de configuracion o si tiene la VPN activada"
        raise SystemExit(msg)
    else:
        print("Conexion exitosa\n")

    # Cursor normal: los fetchall traen listas de tuplas
    curr = conn.cursor()
    curr.execute("set search_path = 'negocio';")

    # Cursor asociativo: los fetchall traen listas de diccionarios con key=columna (es mas lento)
    curr_asoc = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    curr_asoc.execute("set search_path = 'negocio';")

    return curr, curr_asoc, conn


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
    __cursor_asoc = None

    def __init__(self, server_info: dict, usar_logs=False):

        self.__cursor, self.__cursor_asoc, self.__conn = instance_cursor(config_user=server_info.get('username'),
                                                                         config_password=server_info.get('password'),
                                                                         config_host=server_info.get('host'),
                                                                         config_database=server_info.get('dbname'))

    def get_cursor(self):
        return self.__cursor

    def get_cursor_asociativo(self):
        return self.__cursor_asoc

    def ejecutar(self, sql):
        """
        Ejecuta una query, no hace ningún fetch. Para que se vea reflejado en la db se debe hacer un commit.
        """

        print(f'Ejecutando sql: {sql}')
        curr = self.get_cursor()
        try:
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
            print('HACIENDO ROLLBACK')
            self.__conn.rollback()

    def consultar(self, sql: str, asoc=True):
        """
        Consulta en la base haciendo un fetchall.
        Parameters:
            sql (str):      query sql para consultar
            asoc (bool):    indica si retorna la consulta como una lista de diccionarios(asociativo) o tuplas
        """
        if asoc:
            cursor = self.get_cursor_asociativo()
        else:
            cursor = self.get_cursor()

        cursor.execute(sql)
        return cursor.fetchall()

    def consultar_fila(self, sql, asoc=True):
        """Consulta en la base y retorna el primer registro
        Parameters:
            sql (str):      query sql para consultar
            asoc (bool):    indica si retorna la consulta como un diccionario
        """
        if asoc:
            cursor = self.get_cursor_asociativo()
        else:
            cursor = self.get_cursor()

        cursor.execute(sql)
        datos = cursor.fetchone()

        # Contemplo si estoy devolviendo una sola columna
        return datos[0] if datos.__len__() == 1 else datos

    def terminar_conexion(self):
        self.__cursor.close()
        self.__conn.close()
        print("Conexion finalizada")
