class Computer:
    cores = 2
    ram = 2
    disk_space = 1000

    def show_main_parameters(self):
        print(f'{self.cores} ядра, {self.ram}, гига')


# создадим компьютер со свойствамии по умолчанию
computer_1 = Computer()

# создадим компьютер и зададим ему ram
computer_2 = Computer()
computer_2.cores = 4
computer_2.ram = 4

# веведем основные характеристики компьютеров при помощи метода, описанного в классе
computer_1.show_main_parameters()  # выведет "2 ядра, 2 гига"
computer_2.show_main_parameters()  # выведет "4 ядра, 4 гига"
