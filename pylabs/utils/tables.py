import sys


class TablePublisher(object):

    def __init__(self):
        self.tables = []
        self.tables.append(TerminalTable())

    def setData(self, data):
        self.tables[0].setData(data)

    def setRowHeaders(self, headers):
        self.tables[0].setRowHeaders(headers)

    def publish(self):
        self.tables[0].publish()


class TerminalTable(object):
# rows, columns = os.popen('stty size', 'r').read().split()

    def setData(self, data):
        self.data = data

    def setRowHeaders(self, headers):
        self.rowHeaders = headers

    def publish(self):
        for r, row in enumerate(self.data):
            line = self.rowHeaders[r]
            if not isinstance(row, (list, tuple)):
                row = [row]
            for col in row:
                cell = ' {0}'.format(col)
                line += cell
            line += '\n'
            sys.stdout.write(line)
