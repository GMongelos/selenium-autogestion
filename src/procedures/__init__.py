from src.procedures.preinscribirmaterias import preInscribirMaterias


__procs = [preInscribirMaterias]

procs = {str(i): (x.TITULO_CONSOLA, x) for i, x in enumerate(__procs, 1)}
