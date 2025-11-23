def my_factorial(n: int):
    if n == 0 or n == 1:
        return 1
    else:
        return n * my_factorial(n - 1)


def divide_and_conquer(num: int, denum: int):
    if denum == 0:
        raise Exception("denum must not be 0!")
    else:
        return f"conquered {num // denum} times"


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
