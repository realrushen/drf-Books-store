from django.test import TestCase

from store.logic import operations


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(5, 5, '+')
        self.assertEqual(10, result)

    def test_minus(self):
        result = operations(10, 5, '-')
        self.assertEqual(5, result)

    def test_multiply(self):
        result = operations(10, 2, '*')
        self.assertEqual(20, result)