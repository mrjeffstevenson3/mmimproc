from unittest import TestCase
from mock import patch, Mock
import os
import sys


class TableTests(TestCase):

    def setUp(self):
        pass

    def test_TablePublisher_has_TerminalTable(self):
        from pylabs.utils.tables import TablePublisher
        from pylabs.utils.tables import TerminalTable
        tp = TablePublisher()
        self.assertIsInstance(tp.tables[0], TerminalTable)

    def test_TablePublisher_forwards_calls(self):
        from pylabs.utils.tables import TablePublisher
        tp = TablePublisher()
        tp.tables[0] = Mock()
        tp.setData([3,4,5])
        tp.tables[0].setData.assert_called_with([3,4,5])
        tp.setRowHeaders(['a','b','c'])
        tp.tables[0].setRowHeaders.assert_called_with(['a','b','c'])
        tp.publish()
        tp.tables[0].publish.assert_called_with()

    def test_TerminalTable_prints_rows_on_publish(self):
        try:
            from pylabs.utils.tables import TerminalTable
            sys.stdout = Mock()
            tt = TerminalTable()
            tt.setRowHeaders(['a','b'])
            tt.setData([[1,2],[3,4]])
            tt.publish()
            sys.stdout.write.assert_called_with('b 3 4\n') # last call is last row
            sys.stdout.write.assert_any_call   ('a 1 2\n')
        finally:
            sys.stdout = sys.__stdout__
