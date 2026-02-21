from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# SVG Templates para avatares
SVG_TEMPLATES = {
    'smile': '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="40" r="5" fill="currentColor"/><circle cx="65" cy="40" r="5" fill="currentColor"/><path d="M30 60 Q50 75 70 60" stroke="currentColor" stroke-width="5" stroke-linecap="round" fill="none"/></svg>',
    'cat': '<svg viewBox="0 0 100 100" fill="none"><path d="M20 30 L30 15 L35 30 Z" fill="currentColor"/><path d="M80 30 L70 15 L65 30 Z" fill="currentColor"/><circle cx="35" cy="45" r="4" fill="currentColor"/><circle cx="65" cy="45" r="4" fill="currentColor"/><path d="M40 60 L50 65 L60 60" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/><path d="M50 65 L50 55" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>',
    'star-eyes': '<svg viewBox="0 0 100 100" fill="none"><path d="M35 40 L37 46 L43 46 L38 50 L40 56 L35 52 L30 56 L32 50 L27 46 L33 46 Z" fill="currentColor"/><path d="M65 40 L67 46 L73 46 L68 50 L70 56 L65 52 L60 56 L62 50 L57 46 L63 46 Z" fill="currentColor"/><circle cx="50" cy="65" r="8" fill="currentColor"/></svg>',
    'robot': '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="25" width="40" height="45" rx="5" fill="currentColor"/><rect x="35" y="35" width="10" height="10" rx="2" fill="white"/><rect x="55" y="35" width="10" height="10" rx="2" fill="white"/><rect x="40" y="55" width="20" height="5" rx="2" fill="white"/><circle cx="50" cy="20" r="3" fill="currentColor"/><line x1="50" y1="17" x2="50" y2="25" stroke="currentColor" stroke-width="2"/></svg>',
    'heart': '<svg viewBox="0 0 100 100" fill="none"><path d="M35 40 C35 35 30 32 27 35 C24 32 19 35 19 40 C19 45 27 50 27 50 C27 50 35 45 35 40 Z" fill="currentColor"/><path d="M81 40 C81 35 76 32 73 35 C70 32 65 35 65 40 C65 45 73 50 73 50 C73 50 81 45 81 40 Z" fill="currentColor"/><path d="M35 65 Q50 75 65 65" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
    'glasses': '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="42" r="12" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="65" cy="42" r="12" stroke="currentColor" stroke-width="3" fill="none"/><line x1="47" y1="42" x2="53" y2="42" stroke="currentColor" stroke-width="3"/><path d="M35 60 Q50 68 65 60" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
    'music': '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="42" r="4" fill="currentColor"/><circle cx="65" cy="42" r="4" fill="currentColor"/><path d="M40 30 L45 25 L50 30 L55 25 L60 30" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/><path d="M35 60 Q50 72 65 60" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
    'wink': '<svg viewBox="0 0 100 100" fill="none"><line x1="28" y1="40" x2="42" y2="40" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><circle cx="65" cy="40" r="5" fill="currentColor"/><path d="M32 62 Q50 75 68 62" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
    'cool': '<svg viewBox="0 0 100 100" fill="none"><rect x="20" y="35" width="60" height="15" rx="7" fill="currentColor"/><line x1="20" y1="42" x2="15" y2="42" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><line x1="80" y1="42" x2="85" y2="42" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><path d="M38 65 L62 65" stroke="currentColor" stroke-width="4" stroke-linecap="round"/></svg>',
    'bear': '<svg viewBox="0 0 100 100" fill="none"><circle cx="25" cy="25" r="10" fill="currentColor"/><circle cx="75" cy="25" r="10" fill="currentColor"/><circle cx="35" cy="45" r="4" fill="currentColor"/><circle cx="65" cy="45" r="4" fill="currentColor"/><ellipse cx="50" cy="58" rx="8" ry="10" fill="currentColor"/><path d="M42 65 Q50 70 58 65" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/></svg>',
    'lightning': '<svg viewBox="0 0 100 100" fill="none"><path d="M30 35 L38 25 L35 40 L42 40 L34 55 L37 40 L30 40 Z" fill="currentColor"/><path d="M68 35 L60 25 L63 40 L56 40 L64 55 L61 40 L68 40 Z" fill="currentColor"/><path d="M35 65 Q50 75 65 65" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
    'flower': '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="42" r="4" fill="currentColor"/><circle cx="65" cy="42" r="4" fill="currentColor"/><circle cx="30" cy="25" r="6" fill="currentColor"/><circle cx="40" cy="20" r="6" fill="currentColor"/><circle cx="50" cy="18" r="6" fill="currentColor"/><circle cx="60" cy="20" r="6" fill="currentColor"/><circle cx="70" cy="25" r="6" fill="currentColor"/><path d="M35 60 Q50 70 65 60" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
    'alien': '<svg viewBox="0 0 100 100" fill="none"><ellipse cx="35" cy="42" rx="8" ry="12" fill="currentColor"/><ellipse cx="65" cy="42" rx="8" ry="12" fill="currentColor"/><ellipse cx="50" cy="65" rx="15" ry="8" fill="currentColor"/><circle cx="40" cy="20" r="5" fill="currentColor"/><circle cx="60" cy="20" r="5" fill="currentColor"/></svg>',
    'crown': '<svg viewBox="0 0 100 100" fill="none"><path d="M25 25 L35 35 L50 20 L65 35 L75 25 L70 45 L30 45 Z" fill="currentColor"/><circle cx="35" cy="45" r="4" fill="currentColor"/><circle cx="65" cy="45" r="4" fill="currentColor"/><path d="M38 62 Q50 70 62 62" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
    'ninja': '<svg viewBox="0 0 100 100" fill="none"><rect x="20" y="30" width="60" height="25" rx="3" fill="currentColor"/><rect x="28" y="38" width="12" height="8" rx="1" fill="white"/><rect x="60" y="38" width="12" height="8" rx="1" fill="white"/></svg>',
    'party': '<svg viewBox="0 0 100 100" fill="none"><path d="M35 20 L40 35 L45 20 L50 35 L55 20 L60 35 L65 20" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/><circle cx="32" cy="45" r="5" fill="currentColor"/><circle cx="68" cy="45" r="5" fill="currentColor"/><path d="M30 62 Q50 78 70 62" stroke="currentColor" stroke-width="5" stroke-linecap="round" fill="none"/></svg>',
    'rocket': '<svg viewBox="0 0 100 100" fill="none"><path d="M50 15 L60 40 L55 70 L45 70 L40 40 Z" fill="currentColor"/><circle cx="50" cy="50" r="8" fill="white"/><path d="M35 70 L30 80 L40 75 Z" fill="currentColor"/><path d="M65 70 L70 80 L60 75 Z" fill="currentColor"/></svg>',
    'pizza': '<svg viewBox="0 0 100 100" fill="none"><path d="M50 20 L80 70 L20 70 Z" fill="currentColor"/><circle cx="45" cy="45" r="5" fill="white"/><circle cx="60" cy="50" r="5" fill="white"/><circle cx="50" cy="60" r="5" fill="white"/></svg>',
    'coffee': '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="40" width="40" height="35" rx="5" fill="currentColor"/><path d="M35 30 Q40 25 45 30" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 30 Q55 25 60 30" stroke="currentColor" stroke-width="3" fill="none"/><rect x="70" y="50" width="10" height="15" rx="3" fill="currentColor"/></svg>',
    'game': '<svg viewBox="0 0 100 100" fill="none"><rect x="25" y="35" width="50" height="30" rx="8" fill="currentColor"/><circle cx="40" cy="50" r="6" fill="white"/><path d="M65 45 L65 55 M60 50 L70 50" stroke="white" stroke-width="3"/></svg>',
    'book': '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="25" width="40" height="50" rx="3" fill="currentColor"/><path d="M50 25 L50 75" stroke="white" stroke-width="2"/><path d="M35 35 L45 35 M35 45 L45 45 M35 55 L45 55" stroke="white" stroke-width="2"/></svg>',
    'camera': '<svg viewBox="0 0 100 100" fill="none"><rect x="25" y="35" width="50" height="35" rx="5" fill="currentColor"/><circle cx="50" cy="52" r="12" fill="white"/><circle cx="50" cy="52" r="8" fill="currentColor"/><rect x="45" y="28" width="10" height="7" rx="2" fill="currentColor"/></svg>',
    'headphones': '<svg viewBox="0 0 100 100" fill="none"><path d="M30 50 Q30 25 50 25 Q70 25 70 50" stroke="currentColor" stroke-width="5" fill="none"/><rect x="25" y="50" width="10" height="20" rx="3" fill="currentColor"/><rect x="65" y="50" width="10" height="20" rx="3" fill="currentColor"/></svg>',
    'palette': '<svg viewBox="0 0 100 100" fill="none"><ellipse cx="50" cy="50" rx="30" ry="25" fill="currentColor"/><circle cx="40" cy="40" r="4" fill="white"/><circle cx="55" cy="38" r="4" fill="white"/><circle cx="45" cy="52" r="4" fill="white"/><circle cx="60" cy="50" r="4" fill="white"/></svg>',
    'umbrella': '<svg viewBox="0 0 100 100" fill="none"><path d="M50 30 Q30 30 25 45 L50 45 L75 45 Q70 30 50 30" fill="currentColor"/><path d="M50 45 L50 70 Q50 75 55 75" stroke="currentColor" stroke-width="3" fill="none"/></svg>',
    'balloon': '<svg viewBox="0 0 100 100" fill="none"><ellipse cx="50" cy="40" rx="20" ry="25" fill="currentColor"/><path d="M50 65 L50 80" stroke="currentColor" stroke-width="2"/><path d="M45 68 Q50 70 55 68" stroke="currentColor" stroke-width="2" fill="none"/></svg>',
    'plane': '<svg viewBox="0 0 100 100" fill="none"><path d="M50 30 L70 50 L50 55 L30 50 Z" fill="currentColor"/><rect x="48" y="30" width="4" height="40" fill="currentColor"/><path d="M40 65 L50 70 L60 65" fill="currentColor"/></svg>',
    'bicycle': '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="60" r="12" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="65" cy="60" r="12" stroke="currentColor" stroke-width="3" fill="none"/><path d="M35 60 L50 40 L65 60 M50 40 L50 30" stroke="currentColor" stroke-width="3"/></svg>',
    'icecream': '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="35" r="15" fill="currentColor"/><circle cx="40" cy="40" r="12" fill="currentColor"/><circle cx="60" cy="40" r="12" fill="currentColor"/><path d="M40 50 L50 75 L60 50" fill="currentColor"/></svg>',
    'cake': '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="50" width="40" height="25" rx="3" fill="currentColor"/><path d="M40 50 L40 40 M50 50 L50 40 M60 50 L60 40" stroke="currentColor" stroke-width="2"/><ellipse cx="40" cy="38" rx="3" ry="5" fill="currentColor"/><ellipse cx="50" cy="38" rx="3" ry="5" fill="currentColor"/><ellipse cx="60" cy="38" rx="3" ry="5" fill="currentColor"/></svg>',
    'gift': '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="45" width="40" height="30" rx="3" fill="currentColor"/><rect x="25" y="40" width="50" height="8" rx="2" fill="currentColor"/><path d="M50 40 L50 75 M30 40 Q40 30 50 40 Q60 30 70 40" stroke="white" stroke-width="3"/></svg>',
    'trophy': '<svg viewBox="0 0 100 100" fill="none"><path d="M40 30 L40 50 Q40 60 50 60 Q60 60 60 50 L60 30 Z" fill="currentColor"/><rect x="35" y="25" width="30" height="8" rx="2" fill="currentColor"/><path d="M50 60 L50 70 M40 70 L60 70" stroke="currentColor" stroke-width="4"/><path d="M35 30 L25 35 L25 45 L35 45" stroke="currentColor" stroke-width="2" fill="none"/><path d="M65 30 L75 35 L75 45 L65 45" stroke="currentColor" stroke-width="2" fill="none"/></svg>',
    'gem': '<svg viewBox="0 0 100 100" fill="none"><path d="M50 25 L70 40 L60 65 L40 65 L30 40 Z" fill="currentColor"/><path d="M50 25 L50 65 M30 40 L70 40" stroke="white" stroke-width="2"/></svg>',
    'leaf': '<svg viewBox="0 0 100 100" fill="none"><path d="M50 20 Q70 30 70 50 Q70 70 50 80 Q50 50 50 20" fill="currentColor"/><path d="M50 20 L50 80 M50 35 Q60 40 60 50" stroke="white" stroke-width="2"/></svg>',
    'sun': '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="50" r="15" fill="currentColor"/><path d="M50 20 L50 30 M50 70 L50 80 M20 50 L30 50 M70 50 L80 50 M30 30 L35 35 M65 35 L70 30 M30 70 L35 65 M65 65 L70 70" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>',
    'cloud': '<svg viewBox="0 0 100 100" fill="none"><path d="M30 55 Q30 45 40 45 Q40 35 50 35 Q60 35 60 45 Q70 45 70 55 Q70 65 60 65 L40 65 Q30 65 30 55" fill="currentColor"/></svg>',
    'anchor': '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="30" r="8" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 38 L50 70 M35 60 L35 70 Q35 75 50 75 Q65 75 65 70 L65 60" stroke="currentColor" stroke-width="3"/><path d="M40 50 L60 50" stroke="currentColor" stroke-width="3"/></svg>',
    'compass': '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="50" r="25" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 30 L55 50 L50 70 L45 50 Z" fill="currentColor"/><circle cx="50" cy="50" r="4" fill="currentColor"/></svg>',
    'key': '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="50" r="12" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="35" cy="50" r="6" fill="currentColor"/><path d="M47 50 L70 50 L70 45 M70 50 L70 55" stroke="currentColor" stroke-width="3"/></svg>',
    'feather': '<svg viewBox="0 0 100 100" fill="none"><path d="M30 70 Q40 40 50 20 Q60 40 70 70" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 20 L35 35 M50 30 L38 42 M50 40 L40 50 M50 50 L42 58 M50 60 L45 65" stroke="currentColor" stroke-width="2"/><path d="M50 20 L65 35 M50 30 L62 42 M50 40 L60 50 M50 50 L58 58 M50 60 L55 65" stroke="currentColor" stroke-width="2"/></svg>',
}


def lighten_color(color, percent=20):
    """Aclara un color hexadecimal"""
    try:
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        amt = int(2.55 * percent)
        new_rgb = tuple(min(255, max(0, c + amt)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb).upper()
    except:
        return color


@register.simple_tag
def render_avatar(user, size='50px', show_initials=True):
    """
    Renderiza el avatar de un usuario
    
    Args:
        user: Objeto de usuario
        size: Tamaño del avatar (ej: '50px', '100px')
        show_initials: Si mostrar iniciales cuando no hay avatar personalizado
    """
    # Si el usuario tiene avatar personalizado
    if user.avatar_style and user.avatar_bg_color:
        bg_color = user.avatar_bg_color
        lighter_bg = lighten_color(bg_color, 20)
        
        # Verificar si es un avatar de categoría animals (usa imágenes)
        category = getattr(user, 'avatar_category', 'eiwa')
        
        if category == 'animals':
            # Mapeo de estilos de animales a rutas de imágenes
            animal_images = {
                'dog-breed-1': '/static/img/svg/animals/dog-breed-svgrepo-com (1).svg',
                'dog-breed-2': '/static/img/svg/animals/dog-breed-svgrepo-com.svg',
                'dog': '/static/img/svg/animals/dog-svgrepo-com.svg',
                'dog-face': '/static/img/svg/animals/dog-face-svgrepo-com.svg',
                'cat-1': '/static/img/svg/animals/cat-svgrepo-com.svg',
                'cat-2': '/static/img/svg/animals/cat-svgrepo-com (1).svg',
                'cat-smile': '/static/img/svg/animals/cat-with-wry-smile-svgrepo-com.svg',
                'cat-halloween-1': '/static/img/svg/animals/cat-halloween-kitty-svgrepo-com.svg',
                'cat-halloween-2': '/static/img/svg/animals/cat-halloween-kitty-2-svgrepo-com.svg',
                'fox': '/static/img/svg/animals/animal-cute-fox-svgrepo-com.svg',
                'giraffe': '/static/img/svg/animals/giraffe-svgrepo-com.svg',
                'chipmunk': '/static/img/svg/animals/chipmunk-svgrepo-com.svg',
                'otter-1': '/static/img/svg/animals/otter-svgrepo-com.svg',
                'otter-2': '/static/img/svg/animals/otter-svgrepo-com (1).svg',
                'carnivore-4': '/static/img/svg/animals/animal-carnivore-cartoon-4-svgrepo-com.svg',
                'carnivore-6': '/static/img/svg/animals/animal-carnivore-cartoon-6-svgrepo-com.svg',
                'farm-1': '/static/img/svg/animals/animal-cartoon-farm-svgrepo-com.svg',
                'farm-2': '/static/img/svg/animals/animal-cartoon-farm-2-svgrepo-com.svg',
                'fauna-1': '/static/img/svg/animals/animal-cartoon-fauna-svgrepo-com.svg',
                'fauna-3': '/static/img/svg/animals/animal-cartoon-fauna-3-svgrepo-com.svg',
                'fauna-4': '/static/img/svg/animals/animal-cartoon-fauna-4-svgrepo-com.svg',
                'fauna-5': '/static/img/svg/animals/animal-cartoon-fauna-5-svgrepo-com.svg',
            }
            
            img_src = animal_images.get(user.avatar_style, animal_images['dog-breed-1'])
            
            html = f'''
            <div class="user-avatar" style="
                width: {size};
                height: {size};
                border-radius: 50%;
                background: linear-gradient(135deg, {bg_color} 0%, {lighter_bg} 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            ">
                <img src="{img_src}" alt="Avatar" style="
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    padding: 10%;
                ">
            </div>
            '''
        elif category == 'disney':
            # Mapeo de estilos de Disney a rutas de imágenes
            disney_images = {
                'princess-1': '/static/img/svg/disney/Princess1.webp',
                'princess-2': '/static/img/svg/disney/Princess2.webp',
                'princess-3': '/static/img/svg/disney/Princess3.webp',
                'princess-4': '/static/img/svg/disney/Princess4.webp',
                'princess-5': '/static/img/svg/disney/Princess5.webp',
                'princess-6': '/static/img/svg/disney/Princess6.webp',
                'princess-7': '/static/img/svg/disney/Princess7.webp',
                'princess-8': '/static/img/svg/disney/Princess8.webp',
                'princess-9': '/static/img/svg/disney/Princess9.webp',
            }
            
            img_src = disney_images.get(user.avatar_style, disney_images['princess-1'])
            
            html = f'''
            <div class="user-avatar" style="
                width: {size};
                height: {size};
                border-radius: 50%;
                background: linear-gradient(135deg, {bg_color} 0%, {lighter_bg} 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            ">
                <img src="{img_src}" alt="Avatar" style="
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    padding: 10%;
                ">
            </div>
            '''
        else:
            # Avatar de categoría Eiwa (usa SVG templates)
            svg_template = SVG_TEMPLATES.get(user.avatar_style, SVG_TEMPLATES['smile'])
            svg_color = user.avatar_svg_color if hasattr(user, 'avatar_svg_color') and user.avatar_svg_color else '#FFFFFF'
            
            html = f'''
            <div class="user-avatar" style="
                width: {size};
                height: {size};
                border-radius: 50%;
                background: linear-gradient(135deg, {bg_color} 0%, {lighter_bg} 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            ">
                <div style="
                    width: 100%;
                    height: 100%;
                    color: {svg_color};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    {svg_template}
                </div>
            </div>
            '''
    else:
        # Avatar por defecto con iniciales
        if show_initials:
            initials = f"{user.nombre[0]}{user.apellido[0]}" if user.nombre and user.apellido else "?"
            html = f'''
            <div class="user-avatar" style="
                width: {size};
                height: {size};
                border-radius: 50%;
                background: linear-gradient(135deg, var(--azul-pastel), var(--naranja-pastel));
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: calc({size} / 2.5);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            ">
                {initials}
            </div>
            '''
        else:
            html = f'''
            <div class="user-avatar" style="
                width: {size};
                height: {size};
                border-radius: 50%;
                background: linear-gradient(135deg, var(--azul-pastel), var(--naranja-pastel));
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            "></div>
            '''
    
    return mark_safe(html)


@register.simple_tag
def render_avatar_inline(user, size='40px'):
    """
    Renderiza el avatar de un usuario en línea (para usar en listas, comentarios, etc.)
    """
    return render_avatar(user, size=size, show_initials=True)
