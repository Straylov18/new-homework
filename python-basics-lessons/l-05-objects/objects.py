class Computer:
    cores = 2
    ram = 2
    disk_space = 1000
    color = 'gray'

    def __init__(self, cores, ram, disk_space = 0, color = 'gray'):
        self.cores = cores
        self.ram = ram
        self.disk_space = disk_space
        self.color = color

    def show_main_parameters(self):
        print(f'{self.cores} ядра, {self.ram}, гига')

    def __str__(self):
        return f"строковое представление объекта: ({self.cores}, {self.ram}, {self.disk_space}, {self.color})"


# создадим компьютер со свойствамии по умолчанию
computer_1 = Computer(2, 2)

# создадим компьютер и зададим ему cores, ram
computer_2 = Computer(4, 4)
# можно изменять параметры и после создания объекта
# computer_2.cores = 4
# computer_2.ram = 4

# веведем основные характеристики компьютеров при помощи метода, описанного в классе
computer_1.show_main_parameters()  # выведет "2 ядра, 2 гига"
computer_2.show_main_parameters()  # выведет "4 ядра, 4 гига"

# воспользуемся магическим методом перевода в строку
computer_4 = Computer(2, 3)
print(computer_4)  # print автоматически вызывает str(computer_1) метод
# выдаст 'строковое представление объекта: (2, 3, 1000, "gray")'

