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

    def renderizar_menu(self, listaFunciones):
        """
        Renderiza el menu en pantalla y espera un input de usuario que define lo que va a hacer
        """
        print(f'0 : Salir del programa')
        for key in range(0, len(listaFunciones)):
            print(f'{key+1} : {listaFunciones[key][0]}')


        self.separador()

        opcion = input("Elija una opcion: ")
        if not opcion.isdigit() or int(opcion) not in range(0, len(listaFunciones) + 1):
            print("Opcion incorrecta, intente de nuevo")
            self.separador()
            self.renderizar_menu(listaFunciones)
        else:
            print()
            return opcion


consola = Vista()
