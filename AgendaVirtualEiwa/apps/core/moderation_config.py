"""
Configuración de palabras prohibidas para el sistema de moderación INTELIGENTE

El sistema detecta automáticamente:
- Variaciones con números (ej: "put0", "p4to")
- Espacios entre letras (ej: "p u t o")
- Caracteres separadores (ej: "p.u.t.o", "p-u-t-o")
- Letras repetidas (ej: "puuuuto")
- Acentos y variaciones (ej: "púto", "pùto")

Solo necesitas agregar la palabra BASE, el sistema detecta las variaciones.
"""

# Lista de palabras BASE prohibidas
# El sistema detectará automáticamente todas las variaciones
PROHIBITED_WORDS = [
    # Palabras ofensivas/vulgares
    'puto', 'puta', 'pendejo', 'cabron', 'verga',
    'chingar', 'mierda', 'cagar', 'joder', 'coger',
    'coño', 'carajo', 'culo', 'masturbar', 'porno',
    
    # Insultos
    'idiota', 'estupido', 'imbecil', 'retrasado',
    'marica', 'maricon', 'perra', 'zorra',
    
    # Contenido sexual explícito
    'follar', 'mamada', 'pene', 'vagina',
    
    # Drogas
    'droga', 'cocaina', 'marihuana', 'mota',
    
    # Violencia
    'matar', 'asesinar', 'violar',
]

# Excepciones educativas
# Estas palabras NO serán bloqueadas
EDUCATIONAL_EXCEPTIONS = [
    'sexual',  # OK en "educación sexual"
    'sexo',    # OK en "sexo biológico"
    'droga',   # OK en "prevención de drogas"
]
