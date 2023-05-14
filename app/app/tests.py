"""
Sample test
"""

from django.test import SimpleTestCase
from . import calc


class CalcTests(SimpleTestCase):

    def test_add_numbers(self):
        res = calc.add(5, 6)

        self.assertEqual(res, 11)
        print("hi dummy test!")

    def test_calc_number(self):
        res = calc.subtract(10, 2)

        self.assertEquals(res , 5)
    