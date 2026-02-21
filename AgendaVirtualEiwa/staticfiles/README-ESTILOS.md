# Guía de Estilos - Agenda Virtual EIWA

## Colores de la Marca

```css
--azul-principal: rgb(33, 62, 137);      /* Azul oscuro EIWA */
--azul-secundario: rgb(0, 109, 185);     /* Azul medio EIWA */
--azul-pastel: rgb(135, 169, 224);       /* Azul claro/pastel */
--naranja-eiwa: rgb(246, 173, 25);       /* Naranja EIWA */
--naranja-pastel: rgb(255, 209, 128);    /* Naranja claro/pastel */
--blanco: rgb(241, 244, 246);            /* Blanco suave */
--gris-suave: rgb(248, 249, 251);        /* Gris de fondo */
--negro: rgb(1, 1, 1);                   /* Negro */
```

## Tipografías

- **Títulos grandes**: Bebas Neue (sans-serif)
- **Texto general**: Montserrat (sans-serif)

## Componentes Disponibles

### 1. Botones

```html
<!-- Botón primario -->
<button class="btn btn-primary">Texto del Botón</button>

<!-- Botón accent (naranja) -->
<button class="btn btn-accent">Texto del Botón</button>

<!-- Botones hero (más grandes) -->
<button class="btn-hero btn-hero-primary">Crear Cuenta</button>
<button class="btn-hero btn-hero-secondary">Iniciar Sesión</button>
```

### 2. Tarjetas

```html
<div class="card">
    <div class="card-icon">
        <svg><!-- Tu icono SVG aquí --></svg>
    </div>
    <h4 class="card-title">Título</h4>
    <p class="card-description">Descripción de la tarjeta</p>
    <button class="btn btn-primary">Acción</button>
</div>
```

### 3. Sección Hero

```html
<section class="hero">
    <div class="hero-content">
        <h2 class="hero-title">Tu Título Aquí</h2>
        <p class="hero-subtitle">Tu subtítulo aquí</p>
        <div class="hero-decoration"></div>
        <div class="hero-buttons">
            <button class="btn-hero btn-hero-primary">Botón 1</button>
            <button class="btn-hero btn-hero-secondary">Botón 2</button>
        </div>
    </div>
</section>
```

### 4. Secciones de Contenido

```html
<!-- Sección con fondo blanco -->
<section class="section section-white">
    <div class="container">
        <h3 class="section-title">Título de Sección</h3>
        <p class="section-text">Texto de la sección</p>
    </div>
</section>

<!-- Sección con fondo gris -->
<section class="section section-gray">
    <div class="container">
        <!-- Contenido -->
    </div>
</section>
```

### 5. Grid de Tarjetas

```html
<div class="cards">
    <div class="card"><!-- Tarjeta 1 --></div>
    <div class="card"><!-- Tarjeta 2 --></div>
    <div class="card"><!-- Tarjeta 3 --></div>
</div>
```

### 6. Formularios

```html
<div class="form-group">
    <label class="form-label">Nombres</label>
    <input type="text" class="form-input" placeholder="Tu nombre">
</div>

<div class="form-group">
    <label class="form-label">Mensaje</label>
    <textarea class="form-textarea" placeholder="Tu mensaje"></textarea>
</div>
```

### 7. Alertas

```html
<div class="alert alert-success">Operación exitosa</div>
<div class="alert alert-error">Error en la operación</div>
<div class="alert alert-info">Información importante</div>
<div class="alert alert-warning">Advertencia</div>
```

### 8. Badges

```html
<span class="badge badge-primary">Nuevo</span>
<span class="badge badge-accent">Destacado</span>
<span class="badge badge-success">Completado</span>
<span class="badge badge-danger">Urgente</span>
```

## Uso de la Plantilla Base

Para crear una nueva página, extiende de `base.html`:

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Mi Página - Agenda Virtual Eiwa{% endblock %}

{% block extra_css %}
<!-- CSS adicional específico de esta página -->
<style>
    /* Tus estilos aquí */
</style>
{% endblock %}

{% block content %}
<!-- Tu contenido aquí -->
<section class="section section-white">
    <div class="container">
        <h2 class="section-title">Mi Contenido</h2>
    </div>
</section>
{% endblock %}

{% block extra_js %}
<!-- JavaScript adicional específico de esta página -->
<script>
    // Tu código aquí
</script>
{% endblock %}
```

## Animaciones Incluidas

- **fadeInUp**: Aparece desde abajo con fade
- **fadeInWord**: Animación de palabras (usado en hero-title)
- **ripple**: Efecto ripple en botones al hacer click

## Responsive

Todos los componentes son 100% responsive con breakpoints en:
- **768px**: Tablets
- **480px**: Móviles

El logo del header se oculta automáticamente en móviles.

## Iconos SVG Recomendados

Para los iconos de las tarjetas, usa SVG con:
- `viewBox="0 0 24 24"`
- `fill="none"`
- `stroke="currentColor"`
- `stroke-width="2"`

Esto permite que hereden el color del contenedor.
