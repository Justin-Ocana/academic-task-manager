"""
Sistema de moderación de contenido inteligente
Detecta palabras inapropiadas y sus variaciones automáticamente
Similar al sistema de Roblox
"""

import re
from typing import Tuple, List
from .moderation_config import PROHIBITED_WORDS, EDUCATIONAL_EXCEPTIONS


class ContentModerator:
    """Moderador de contenido inteligente para filtrar palabras inapropiadas"""
    
    # Cargar palabras base desde el archivo de configuración
    BASE_PROHIBITED_WORDS = PROHIBITED_WORDS
    EDUCATIONAL_EXCEPTIONS = EDUCATIONAL_EXCEPTIONS
    
    # Caracteres comunes usados para evadir filtros
    LEET_SPEAK = {
        'a': ['a', '4', '@', 'á', 'à', 'â', 'ä'],
        'e': ['e', '3', 'é', 'è', 'ê', 'ë'],
        'i': ['i', '1', '!', 'í', 'ì', 'î', 'ï'],
        'o': ['o', '0', 'ó', 'ò', 'ô', 'ö'],
        'u': ['u', 'ú', 'ù', 'û', 'ü'],
        's': ['s', '5', '$', 'z'],
        't': ['t', '7', '+'],
        'l': ['l', '1', '|'],
        'g': ['g', '9', 'q'],
        'b': ['b', '8'],
    }
    
    @classmethod
    def check_content(cls, text: str, field_name: str = "contenido") -> Tuple[bool, str, List[str]]:
        """
        Verifica si el contenido contiene palabras prohibidas o sus variaciones
        
        Args:
            text: Texto a verificar
            field_name: Nombre del campo (para el mensaje de error)
            
        Returns:
            Tuple[bool, str, List[str]]: (es_valido, mensaje_error, palabras_encontradas)
        """
        if not text:
            return True, "", []
        
        # Normalizar texto
        normalized_text = cls._normalize_text(text.lower())
        
        # Buscar palabras prohibidas y sus variaciones
        found_words = []
        for base_word in cls.BASE_PROHIBITED_WORDS:
            # Verificar si es una excepción educativa
            if base_word in cls.EDUCATIONAL_EXCEPTIONS:
                continue
            
            # Detectar la palabra y sus variaciones
            if cls._detect_word_variations(base_word, normalized_text):
                found_words.append(base_word)
        
        if found_words:
            message = (
                f"El {field_name} contiene lenguaje inapropiado. "
                "Por favor, mantén un lenguaje apropiado y profesional."
            )
            return False, message, found_words
        
        return True, "", []
    
    @classmethod
    def _detect_word_variations(cls, word: str, text: str) -> bool:
        """
        Detecta una palabra y sus variaciones (leet speak, espacios, etc.)
        
        Args:
            word: Palabra base a buscar
            text: Texto donde buscar
            
        Returns:
            bool: True si se encontró la palabra o alguna variación
        """
        # 1. Buscar palabra exacta
        if re.search(r'\b' + re.escape(word) + r'\b', text):
            return True
        
        # 2. Buscar con espacios entre letras (ej: "p u t o")
        spaced_pattern = r'\b' + r'\s*'.join(re.escape(c) for c in word) + r'\b'
        if re.search(spaced_pattern, text):
            return True
        
        # 3. Buscar variaciones con leet speak (ej: "put0", "p4to")
        leet_pattern = cls._generate_leet_pattern(word)
        if re.search(leet_pattern, text):
            return True
        
        # 4. Buscar sin espacios pero con caracteres extra (ej: "p.u.t.o", "p-u-t-o")
        separated_pattern = r'\b' + r'[\s\.\-_]*'.join(re.escape(c) for c in word) + r'\b'
        if re.search(separated_pattern, text):
            return True
        
        # 5. Buscar repeticiones de letras (ej: "puuuuto", "puttto")
        repeated_pattern = cls._generate_repeated_pattern(word)
        if re.search(repeated_pattern, text):
            return True
        
        return False
    
    @classmethod
    def _generate_leet_pattern(cls, word: str) -> str:
        """
        Genera un patrón regex que detecta variaciones leet speak
        
        Args:
            word: Palabra base
            
        Returns:
            str: Patrón regex
        """
        pattern_parts = []
        for char in word.lower():
            if char in cls.LEET_SPEAK:
                # Crear grupo de alternativas para esta letra
                alternatives = '|'.join(re.escape(alt) for alt in cls.LEET_SPEAK[char])
                pattern_parts.append(f'(?:{alternatives})')
            else:
                pattern_parts.append(re.escape(char))
        
        # Permitir espacios/caracteres opcionales entre letras
        pattern = r'\b' + r'[\s\.\-_]*'.join(pattern_parts) + r'\b'
        return pattern
    
    @classmethod
    def _generate_repeated_pattern(cls, word: str) -> str:
        """
        Genera un patrón que detecta letras repetidas
        
        Args:
            word: Palabra base
            
        Returns:
            str: Patrón regex
        """
        pattern_parts = []
        for char in word.lower():
            # Permitir que cada letra se repita 1-5 veces
            pattern_parts.append(re.escape(char) + r'{1,5}')
        
        pattern = r'\b' + ''.join(pattern_parts) + r'\b'
        return pattern
    
    @classmethod
    def _normalize_text(cls, text: str) -> str:
        """
        Normaliza el texto para comparación
        
        Args:
            text: Texto a normalizar
            
        Returns:
            str: Texto normalizado
        """
        # Reemplazar caracteres con acentos
        replacements = {
            'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ñ': 'n',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @classmethod
    def censor_text(cls, text: str) -> str:
        """
        Censura palabras inapropiadas reemplazándolas con ###
        Estilo Roblox
        
        Args:
            text: Texto a censurar
            
        Returns:
            str: Texto censurado
        """
        if not text:
            return text
        
        censored_text = text
        normalized_for_check = cls._normalize_text(text.lower())
        
        for base_word in cls.BASE_PROHIBITED_WORDS:
            # Verificar si es una excepción educativa
            if base_word in cls.EDUCATIONAL_EXCEPTIONS:
                continue
            
            # Encontrar todas las ocurrencias de la palabra y sus variaciones
            censored_text = cls._censor_word_variations(base_word, censored_text, normalized_for_check)
        
        return censored_text
    
    @classmethod
    def _censor_word_variations(cls, word: str, text: str, normalized_text: str) -> str:
        """
        Censura una palabra y sus variaciones en el texto
        
        Args:
            word: Palabra base a censurar
            text: Texto original
            normalized_text: Texto normalizado para búsqueda
            
        Returns:
            str: Texto con la palabra censurada
        """
        import re
        
        # Buscar todas las variaciones de la palabra
        # Generar patrón que capture la palabra completa
        leet_pattern = cls._generate_leet_pattern(word)
        
        # Encontrar todas las coincidencias en el texto normalizado
        matches = list(re.finditer(leet_pattern, normalized_text, re.IGNORECASE))
        
        # Reemplazar de atrás hacia adelante para no afectar los índices
        for match in reversed(matches):
            start, end = match.span()
            # Reemplazar con ### del mismo largo que la palabra encontrada
            censored = '#' * (end - start)
            text = text[:start] + censored + text[end:]
        
        return text
    
    @classmethod
    def moderate_task(cls, title: str, description: str = "", mode: str = "block") -> Tuple[bool, str, str, str]:
        """
        Modera el contenido de una tarea
        
        Args:
            title: Título de la tarea
            description: Descripción de la tarea
            mode: Modo de moderación ('off', 'censor', 'block')
            
        Returns:
            Tuple[bool, str, str, str]: (es_valido, mensaje_error, titulo_censurado, descripcion_censurada)
        """
        # Si está desactivada, no hacer nada
        if mode == 'off':
            return True, "", title, description
        
        # Modo censurar: reemplazar palabras con ###
        if mode == 'censor':
            censored_title = cls.censor_text(title)
            censored_description = cls.censor_text(description) if description else ""
            return True, "", censored_title, censored_description
        
        # Modo bloquear: no permitir guardar
        if mode == 'block':
            # Verificar título
            is_valid, error_msg, _ = cls.check_content(title, "título")
            if not is_valid:
                return False, error_msg, title, description
            
            # Verificar descripción
            if description:
                is_valid, error_msg, _ = cls.check_content(description, "descripción")
                if not is_valid:
                    return False, error_msg, title, description
            
            return True, "", title, description
        
        return True, "", title, description
