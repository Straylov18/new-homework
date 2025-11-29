def get_dominant_color(r: int, g: int, b: int) -> str:
    max_color = max(r, g, b)
    max_colors = []
    if r == g and g == b:
        return 'same'
    if max_color == r:
        max_colors.append('red')
    if max_color == g:
        max_colors.append('green')
    if max_color == b:
        max_colors.append('blue')
    return ', '.join(max_colors)
