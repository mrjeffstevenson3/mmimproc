from unittest import TestCase
from mock import patch, call, Mock, MagicMock
import os


class WorkingContextTests(TestCase):

    def setUp(self):
        pass

    def test_If_target_directory_is_not_current_switches_and_back(self):
        from pylabs.utils._context import WorkingContext
        d1 = '/tmp/current'
        d2 = '/tmp/bla'
        with patch('pylabs.utils._context.os') as osm:
            osm.getcwd.return_value = d1
            with WorkingContext(d1):
                assert not osm.chdir.called
            assert not osm.chdir.called
            with WorkingContext(d2):
                osm.chdir.assert_called_with(d2)
            osm.chdir.assert_called_with(d1)

    def test_If_exception_occurs_changes_back_anyway(self):
        from pylabs.utils._context import WorkingContext
        d1 = '/tmp/current'
        d2 = '/tmp/bla'
        with patch('pylabs.utils._context.os') as osm:
            osm.getcwd.return_value = d1
            try:
                with WorkingContext(d2):
                    osm.chdir.assert_called_with(d2)
                    raise ValueError
            except ValueError:
                osm.chdir.assert_called_with(d1)

    def test_If_newdir_doesnt_exist_creates_it(self):
        from pylabs.utils._context import WorkingContext
        d1 = '/tmp/current'
        d2 = '/tmp/bla'
        with patch('pylabs.utils._context.os') as osm:
            osm.getcwd.return_value = d1
            osm.path.isdir.return_value = False
            with WorkingContext(d2):
                osm.makedirs.assert_called_with(d2)



