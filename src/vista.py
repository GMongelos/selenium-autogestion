"""Modulo que abstrae las distintas interacciones con el usuario por consola"""


class Vista:
    """
    Clase que encapsula los renderizados de elementos por consola
    """

    @staticmethod
    def separador(text=''):
        """
        Imprime por pantalla una linea divisora, a modo de ayuda visual
        """
        if text:
            print(f"\n{text}")
        print('-' * 50)
        print()

    def renderizar_menu(self, procedures: dict):
        """
        Renderiza el menu en pantalla y espera un input de usuario que define lo que va a hacer
        """
        print(f'0 : Salir del programa')
        for item in procedures.items():
            print(f'{item[0]} : {item[1][0]}')

        self.separador()

        opcion = input("Elija una opcion: ")
        if not opcion.isdigit() or int(opcion) not in range(0, len(procedures) + 1):
            print("Opcion incorrecta, intente de nuevo")
            self.separador()
            self.renderizar_menu(procedures)
        else:
            return opcion


consola = Vista()
