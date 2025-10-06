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
        return f"компьютер: ({self.cores}, {self.ram}, {self.disk_space}, {self.color})"


# создадим компьютер, задав ему только обязательные свойства в конструкторе
computer_1 = Computer(2, 2)
print(computer_1)  # выдаст 'компьютер: (2, 2, 0, gray)'


class Notebook(Computer):
    batteryLevel = 100

    def recharge(self):
        self.batteryLevel = 100

    def use(self):
        self.batteryLevel -= self.ram + 2*self.cores  # энергия расходуется больше, если ядер и оперативки больше

    def show_battery_level(self):
        print(f'{self.batteryLevel} %')

    def __str__(self):
        return f"ноутбук: ({self.cores}, {self.ram}, {self.disk_space}, {self.color}, {self.batteryLevel} %)"


notebook_1 = Notebook(4, 4)
print(notebook_1)  # выдаст 'ноутбук: (4, 4, 0, gray, 100 %)'
notebook_1.show_battery_level()  # выдаст '100 %'
notebook_1.use()
notebook_1.show_battery_level()  # выдаст '88 %'
notebook_1.recharge()
notebook_1.show_battery_level()  # выдаст '100 %'

# можно также вызывать параметры и методы родительского класса
notebook_1.show_main_parameters()  # выдаст '4 ядра, 4, гига'
