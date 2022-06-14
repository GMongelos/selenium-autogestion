"""Modulo que hace cosas como un logger"""

import os
import logging
import time

EXIT_STRING = ("-" * 10) + " APLICACION TERMINADA " + ("-" * 10)
LOGS_FOLDERNAME = 'logs'


class Logger:
    logs_path = os.path.join(os.getcwd(), LOGS_FOLDERNAME)

    def __init__(self,
                 name: str = __name__,
                 log_filename: str = 'default.log',
                 level: logging = logging.DEBUG,
                 es_thread=False):
        """
        Clase que encapsula el modulo logging.

        :param name: Nombre del objeto, aparecerá así en el archivo
        :param log_filename: Nombre del archivo .log
        :param level: Nivel de logs, por defecto está seteado en DEBUG
        :param es_thread: Configura el formato dependiendo de si la instancia pertenece a un thread
        """

        # Este atributo se utiliza cuando se requiere un log multilínea
        self.mensaje_compuesto = None
        self.stopwatch = None

        log_filename += '.log' if not log_filename.endswith('.log') else ''

        # Creo la carpeta de logs
        os.makedirs(self.logs_path, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Configuro el formato y el path al handler, si es thread que en el log aparezca el id del thread
        if es_thread:
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(threadName)s: %(message)s')
        else:
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s | %(module)s: %(message)s')
        file_handler = logging.FileHandler(os.path.join(self.logs_path, log_filename))
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def loguear_debug(self, mensaje: str):
        self.logger.debug(mensaje)

    def loguear_info(self, mensaje: str):
        self.logger.info(mensaje)

    def loguear_warning(self, mensaje: str):
        self.logger.warning(mensaje)

    def loguear_error(self, mensaje: str):
        self.logger.error(mensaje)

    def loguear_critical(self, mensaje: str):
        self.logger.critical(mensaje)

    def loguear_exepcion(self, mensaje: str):
        self.logger.exception(mensaje)

    def loguear_exit(self):
        self.loguear_info(EXIT_STRING)

    def log_compuesto_iniciar(self, header: str):
        """
        Comienza el armado de un log compuesto, util cuando se necesita loguear varios datos en un solo entry.

        :param header: Titulo del log
        """
        if self.mensaje_compuesto:
            raise Exception('Error, no se pueden iniciar varios logs compuestos al mismo tiempo')
        else:
            self.mensaje_compuesto = header
            self.stopwatch = time.perf_counter()

    def log_compuesto_add(self, item: str):
        """
        Agrega un item al log compuesto, si este no está iniciado tira un error.

        :param item: Texto para agregar al log
        """
        if not self.mensaje_compuesto:
            raise Exception('Error, no se puede agregar un item a un log compuesto que no esta iniciado')
        else:
            self.mensaje_compuesto += '\n\t' + item

    def log_compuesto_commit(self, last_item: str = None):
        """
        Confirma y escribe el log compuesto al archivo, luego limpia el mensaje compuesto.

        :param last_item: Ultimo item a ser agregado, si no se especifica ninguno, se escribe
        solo el tiempo que tardó en generarse el log compuesto
        :return:
        """
        # Calculo el tiempo de ejecucion
        tiempo_total = round(time.perf_counter() - self.stopwatch, 3)
        tiempo_total_msg = f'[{tiempo_total} seg]'

        if last_item:
            self.mensaje_compuesto += '\n\t' + last_item + tiempo_total_msg
        else:
            self.mensaje_compuesto += '\n\t' + tiempo_total_msg

        # Escribo el log y reseteo el mensaje compuesto
        self.logger.info(self.mensaje_compuesto)
        self.mensaje_compuesto = None
