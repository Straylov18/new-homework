from sub_package.file_for_imports import print_city_population

# вызываем импортированную функцию
print_city_population("Novosibirsk")
print_city_population("New-York")

if __name__ == '__main__':
    print("запустили main.py")
else:
    print("main.py импортировали")
