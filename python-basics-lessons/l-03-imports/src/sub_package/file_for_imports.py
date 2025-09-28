cities = {
    "Moscow": 12,
    "St.Petersburg": 5,
    "Vladivostok": 13,
    "Novosibirsk": 1.5,
    "Krasnoyarsk": 1,
}


def print_city_population(city_name):
    if cities.get(city_name, None) is not None:
        print(f"население {city_name}: {cities[city_name]}")
    else:
        print(f"города {city_name} нет в базе данных")
