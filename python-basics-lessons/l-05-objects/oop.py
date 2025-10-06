class Computer:
    _cores = 2
    _ram = 2
    _disk_space = 1000
    _color = 'gray'

    def __init__(self, cores, ram, disk_space = 0, color = 'gray'):
        self._cores = cores
        self._ram = ram
        self._disk_space = disk_space
        self._color = color

    def get_color(self):
        return self._color

    def show_main_parameters(self):
        print(f'{self._cores} ядра, {self._ram}, гига')

    def __str__(self):
        return f"компьютер: ({self._cores}, {self._ram}, {self._disk_space}, {self._color})"


# создадим компьютер, задав ему только обязательные свойства в конструкторе
computer_1 = Computer(2, 2)
print(computer_1)  # выдаст 'компьютер: (2, 2, 0, gray)'


class Notebook(Computer):
    _batteryLevel = 100

    def recharge(self):
        self._batteryLevel = 100

    def use(self):
        self._batteryLevel -= self._ram + 2*self._cores  # энергия расходуется больше, если ядер и оперативки больше

    def show_battery_level(self):
        print(f'{self._batteryLevel} %')

    def __str__(self):
        return f"ноутбук: ({self._cores}, {self._ram}, {self._disk_space}, {self._color}, {self._batteryLevel} %)"


notebook_1 = Notebook(4, 4)
print(notebook_1)  # выдаст 'ноутбук: (4, 4, 0, gray, 100 %)'
notebook_1.show_battery_level()  # выдаст '100 %'
notebook_1.use()
notebook_1.show_battery_level()  # выдаст '88 %'
notebook_1.recharge()
notebook_1.show_battery_level()  # выдаст '100 %'

# можно также вызывать параметры и методы родительского класса
notebook_1.show_main_parameters()  # выдаст '4 ядра, 4, гига'
