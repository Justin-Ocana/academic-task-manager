# Sistema de Moderación de Contenido INTELIGENTE 🛡️

## ¿Qué hace?

Sistema de moderación **inteligente** similar al de Roblox que detecta automáticamente palabras inapropiadas y **todas sus variaciones**.

## 🎮 Modos de Moderación (Configurable por Grupo)

Cada grupo puede elegir su nivel de moderación:

### 1. **Desactivada** (`off`)
- No se aplica ningún filtro
- Los usuarios pueden escribir libremente
- Útil para grupos de confianza

### 2. **Censurar** (`censor`) - ⭐ ESTILO ROBLOX
- Las palabras inapropiadas se reemplazan con `###`
- La tarea se guarda con el contenido censurado
- Ejemplo: "masturbar perros" → "######## perros"
- **Modo recomendado** - Permite expresión pero mantiene apropiado

### 3. **Bloquear** (`block`)
- No permite guardar contenido con palabras inapropiadas
- Muestra mensaje de error
- Modo más estricto

## 🧠 Detección Inteligente

El sistema detecta automáticamente:

### ✅ Variaciones con números (Leet Speak)
- `puto` → `put0`, `p4to`, `pu70`
- `idiota` → `1d1ota`, `idi0ta`

### ✅ Espacios entre letras
- `puto` → `p u t o`, `p  u  t  o`

### ✅ Caracteres separadores
- `puto` → `p.u.t.o`, `p-u-t-o`, `p_u_t_o`

### ✅ Letras repetidas
- `puto` → `puuuuto`, `puttto`, `putooo`

### ✅ Acentos y variaciones
- `puto` → `púto`, `pùto`, `pûto`

### ✅ Combinaciones
- `puto` → `p4.u.t0`, `p u 7 0`

## 🎯 ¿Cómo funciona?

1. **Al crear/editar tarea**: Verifica título y descripción
2. **Detecta variaciones**: Busca la palabra y TODAS sus variaciones
3. **Bloquea si encuentra**: Muestra mensaje amigable

## 💬 Mensaje al usuario

> "El contenido contiene lenguaje inapropiado. Por favor, mantén un lenguaje apropiado y profesional."

## ⚙️ Configuración SIMPLE

Solo necesitas agregar la **palabra BASE**, el sistema detecta las variaciones automáticamente.

### Agregar palabras prohibidas

Edita `moderation_config.py`:

```python
PROHIBITED_WORDS = [
    'palabra',  # El sistema detecta: p4l4br4, p a l a b r a, etc.
]
```

### Agregar excepciones educativas

```python
EDUCATIONAL_EXCEPTIONS = [
    'sexual',  # OK en "educación sexual"
    'droga',   # OK en "prevención de drogas"
]
```

## 📊 Ventajas vs Sistema Básico

| Característica | Sistema Básico | Sistema Inteligente |
|----------------|----------------|---------------------|
| Detecta "puto" | ✅ | ✅ |
| Detecta "put0" | ❌ | ✅ |
| Detecta "p u t o" | ❌ | ✅ |
| Detecta "p.u.t.o" | ❌ | ✅ |
| Detecta "puuuto" | ❌ | ✅ |
| Palabras a agregar | Muchas | Pocas |

## 📁 Archivos del sistema

- `moderation.py` - Motor inteligente de detección
- `moderation_config.py` - Lista simple de palabras base
- `MODERATION_README.md` - Esta documentación

## ⚠️ Notas importantes

- **Mucho más efectivo** que un filtro básico
- Detecta la mayoría de intentos de evasión
- No es 100% perfecto (ningún sistema lo es)
- Considera agregar sistema de reportes como respaldo
- Revisa la lista periódicamente

## 🚀 Ejemplo de uso

```python
from apps.core.moderation import ContentModerator

# Modo bloquear
is_valid, error_msg, _, _ = ContentModerator.moderate_task(
    title="Tarea de Matemáticas",
    description="Resolver ejercicios",
    mode="block"
)

# Modo censurar (estilo Roblox)
is_valid, _, censored_title, censored_desc = ContentModerator.moderate_task(
    title="masturbar perros",
    description="Contenido inapropiado",
    mode="censor"
)
# censored_title = "######## perros"
# censored_desc = "Contenido inapropiado" (si no tiene palabras malas)
```

## ⚙️ Configurar en un Grupo

Los líderes pueden configurar el modo de moderación en:
**Configuración del Grupo → Moderación de contenido**

Opciones:
- **Desactivada**: Sin filtros
- **Censurar palabras (###)**: Estilo Roblox (recomendado)
- **Bloquear contenido**: Modo estricto
