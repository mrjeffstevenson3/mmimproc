import sys


class TablePublisher(object):

    def __init__(self):
        self.tables = []
        self.tables.append(TerminalTable())

    def setData(self, data):
        self.tables[0].setData(data)


class TerminalTable(object):
# rows, columns = os.popen('stty size', 'r').read().split()

    def setData(self, data):
        for row in data:
            line = ''
            if not isinstance(row, (list, tuple)):
                row = [row]
            for col in row:
                cell = ' {0}'.format(col)
                line += cell
            line += '\n'
            sys.stdout.write(line)
