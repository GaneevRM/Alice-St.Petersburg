class Tariff:
    name = ''
    cost = 0

    def __init__(self, name, cost):
        self.name = name
        self.cost = cost

    def display_info(self):
        text = self.name + '.' + '\n' + 'Стоимость ' + self.cost + ' рублей. ' + '\n\n'
        return text

class Hall:
    nameHall = ''
    openTime = ''
    closeTimeEnter = ''
    closeTimeExit = ''
    closed = False

    def __init__(self, nameHall, openTime, closeTimeEnter, closeTimeExit, closed):
        self.nameHall = nameHall
        self.openTime = openTime
        self.closeTimeEnter = closeTimeEnter
        self.closeTimeExit = closeTimeExit
        self.closed = closed

    def display_info(self):
        if self.closed:
            text = self.nameHall + '.' + '\n' + 'Станция закрыта. Попробуйте проверить ограничения на данной станции.' + '\n\n'
            return text
        else:
            text = self.nameHall + '.' + '\n' + 'Время открытия ' + self.openTime + '\n' + 'Время закрытия на вход ' + self.closeTimeEnter + '\n' + 'Время закрытия на выход ' + self.closeTimeExit + '\n\n'
        return text

class Problem:
    nameHall = ''
    number = ''
    nameProblem = ''
    date = ''
    time = ''

    def __init__(self, nameHall, number, nameProblem, date, time):
        self.nameHall = nameHall
        self.number = number
        self.nameProblem = nameProblem
        self.date = date
        self.time = time

    def display_info(self):
        text = self.nameHall + '. ' + 'Номер линии - ' + self.number + '.' + '\n' + 'Ограничения: ' + self.nameProblem + '\n' + 'Дни проведения работ: ' + self.date + '\n' + 'Дата окончания работ: ' + self.time + '\n\n'
        return text