import unittest, math, random
from src.checks.DataFileCheck import compare_numbers

class NumberComparisonTest(unittest.TestCase):

    def setUp(self):
        random.seed(823468228)

    def test_equal_integer(self):
        self.assertTupleEqual(compare_numbers(1, 1), (True, 1, math.inf))
        
    def test_equal_float(self):
        self.assertTupleEqual(compare_numbers(1.0, 1.0), (True, 1.0, math.inf))

    def test_integer_precision_10(self):
        self.assertTupleEqual(compare_numbers(123456789, 123456788), (False, 10, -1))

    def test_integer_precision_100(self):
        self.assertTupleEqual(compare_numbers(123456789, 123456798), (False, 100, -1))

    def test_integer_precision_dynamic(self):
        # NOTE: 17 is the maximum precision supported for integers

        # iterate over integers with 1 to 16 digits
        for scale in range(1, 17):

            # generate a random integer with `scale` digits
            a = random.randint(10**scale, 10**(scale+1)-1)

            # apply an error to any digit
            for error in range(1, scale):
                
                # extract the digit at index `error`
                ne = a % 10**(error+1) // 10**error

                # calculate a random, non-zero delta for digit at index `error`
                d = 0
                while d == 0: 
                    d = (10 ** error) * random.randint(-ne, 9-ne)

                # apply delta to digit at index `error`
                b = a + d

                # compare numbers
                #  the expected result is 10**(error + 1) because if the error is eg. in the 10th, the 100th is the most accurate digit
                self.assertTupleEqual(compare_numbers(a, b), (False, 10**(error + 1), -1))

    def test_special(self):
        a = 69809588409 
        b = 69869588409

        self.assertTupleEqual(compare_numbers(a, b), (False, 100000000, -1))

    def test_float_precision_p1(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.23456788), (False, 1, 7))

    def test_float_precision_p2(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.23456798), (False, 1, 6))

    def test_float_precision_p3(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.23456889), (False, 1, 5))

    def test_float_precision_p4(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.23457789), (False, 1, 4))

    def test_float_precision_p5(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.23466789), (False, 1, 3))

    def test_float_precision_p6(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.23556789, verbose=True), (False, 1, 2))

    def test_float_precision_p7(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.24556789), (False, 1, 1))

    def test_float_precision_p8(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 1.34556789), (False, 1, 0))

    def test_scale_missmatch(self):
        self.assertTupleEqual(compare_numbers(1.23456789, 12.3456789), (False, -1, -1))