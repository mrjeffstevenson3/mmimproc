from unittest import TestCase
from mock import patch, call, Mock, MagicMock
import numpy
from numpy.testing import assert_array_equal, assert_array_almost_equal


class T1ModelTests(TestCase):

    def test_against_spreadsheet_values():
        from pylabs.qt1.model import expectedT1
        self.assertEqual(412, expectedT1(T=300, gel=2.28, gado=0.34))

