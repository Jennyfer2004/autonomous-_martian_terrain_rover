ACCIONES_PLANIFICADOR = [
    {
        'nombre': 'ir_a_poi',
        # Precondición: tener energía para al menos un paso
        'precondiciones': lambda estado, contexto, poi: estado['energia'] > 0,
        # Los efectos se calcularán dinámicamente en simulacion
        'efectos': None, 
    },
    {
        'nombre': 'ir_a_base',
        'precondiciones': lambda estado, contexto, base: estado['energia'] > 0  and estado['posicion'] != base,
        'efectos': None,
    },
    {
        'nombre': 'recargar',
        'precondiciones': lambda estado, contexto, base: estado['posicion'] == base and estado['energia'] <  30 ,
        'efectos': lambda estado, contexto, base: {
            'energia': estado['bateria_max'],
        },
        'coste': 0, # Coste fijo de la acción de recargar
        'tiempo': 10 # Tiempo fijo de la acción de recargar
    },
    {
        'nombre': 'dejar_muestras', 
        'precondiciones': lambda estado, contexto, punto:  len(estado['muestras_recolectadas']) > 0 ,
        'efectos': lambda estado, contexto, punto: {
            # 'muestras_recolectadas': set(),
            'muestras_analizadas': estado['muestras_analizadas'] | estado['muestras_recolectadas']
        },
        'coste': 5,
        'tiempo': 8
    }]