import sys


class TablePublisher(object):
    """Abstract class that forwards table generation calls to specific Tables.

        Currently uses only TerminalTable.
    """

    def __init__(self):
        self.tables = []
        self.tables.append(TerminalTable())

    def setData(self, data):
        self.tables[0].setData(data)

    def setRowHeaders(self, headers):
        self.tables[0].setRowHeaders(headers)

    def setColumnHeaders(self, headers):
        self.tables[0].setColumnHeaders(headers)

    def publish(self):
        self.tables[0].publish()


class TerminalTable(object):
    """Implements Table interface to print out a table on the commandline.

        Limited by the number of rows in the terminal.
    """
# rows, columns = os.popen('stty size', 'r').read().split()

    def setData(self, data):
        self.data = data

    def setRowHeaders(self, headers):
        self.rowHeaders = headers

    def setColumnHeaders(self, headers):
        self.colHeaders = headers

    def publish(self):
        rowheaderwidth = len(max(self.rowHeaders, key=len))
        line = ' '*rowheaderwidth
        line += ' '+' '.join(self.colHeaders)+'\n'
        sys.stdout.write(line)
        rows, cols = self.data.shape
        for r in range(rows):
            line = self.rowHeaders[r].ljust(rowheaderwidth)
            for c in range(cols):
                cell = ' {0}'.format(self.data[r,c])
                line += cell
            line += '\n'
            sys.stdout.write(line)
