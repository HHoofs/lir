import numpy
import unittest

from sklearn.linear_model import LogisticRegression

from liar.lr import *


class TestLR(unittest.TestCase):
    def test_probability_fraction(self):
        value_range = [0, 10]
        points_h0 = [ 1, 2, 4, 8 ]
        points_h1 = [ 2, 6, 8, 9 ]

        pfunc = probability_fraction(points_h0, class_value=0, value_range=value_range)
        for point, expected_p in zip(range(11), [ 1., 1., .8, .6, .6, .4, .4, .4, .4, .2, .2 ]):
            self.assertAlmostEqual(expected_p, pfunc.probability(point))

        pfunc = probability_fraction(points_h1, class_value=1, value_range=value_range)
        for point, expected_p in zip(range(11), [ .2, .2, .4, .4, .4, .4, .6, .6, .8, 1, 1 ]):
            self.assertAlmostEqual(expected_p, pfunc.probability(point))

        pfunc = probability_fraction(points_h0, class_value=0, value_range=value_range, remove_from_reference_points=True)
        for point, expected_p in zip(points_h0, [ 1.,  .75, .5, .25 ]):
            self.assertAlmostEqual(expected_p, pfunc.probability(point))

        pfunc = probability_fraction(points_h1, class_value=1, value_range=value_range, remove_from_reference_points=True)
        for point, expected_p in zip(points_h1, [ .25,  .5, .75, 1. ]):
            self.assertAlmostEqual(expected_p, pfunc.probability(point))

    def test_calibrate_lr(self):
        points_h0 = [ 1, 2, 4, 8 ]
        points_h1 = [ 2, 6, 8, 9 ]
        for point, expected_lr in zip(range(11), [ .2, .2, .5, 2/3., 2/3., 1, 1.5, 1.5, 2, 5, 5 ]):
            pfunc = probability_fraction(value_range=[0, 10])
            pfunc0 = pfunc(points=points_h0, class_value=0)
            pfunc1 = pfunc(points=points_h1, class_value=1)
            self.assertAlmostEqual(expected_lr, calibrate_lr(point, pfunc0, pfunc1))

    def test_calibrate_cllr(self):
        points0 = [ 1, 2, 4, 8 ]
        points1 = [ 2, 6, 8, 9 ]
        pfunc = probability_fraction(value_range=[0, 10])
        self.assertAlmostEqual(0.9495230001821591   , calibrated_cllr(points0, points1, pfunc).cllr)

    def test_calculate_cllr(self):
        self.assertAlmostEqual(1, calculate_cllr([1, 1], [1, 1]).cllr)
        self.assertAlmostEqual(2, calculate_cllr([3.]*2, [1/3.]*2).cllr)
        self.assertAlmostEqual(2, calculate_cllr([3.]*20, [1/3.]*20).cllr)
        self.assertAlmostEqual(0.4150374992788437, calculate_cllr([1/3.]*2, [3.]*2).cllr)
        self.assertAlmostEqual(0.7075187496394219, calculate_cllr([1/3.]*2, [1]).cllr)
        self.assertAlmostEqual(0.507177646488535, calculate_cllr([1/100.]*100, [1]).cllr)
        self.assertAlmostEqual(0.5400680236656377, calculate_cllr([1/100.]*100 + [100], [1]).cllr)
        self.assertAlmostEqual(0.5723134914863265, calculate_cllr([1/100.]*100 + [100]*2, [1]).cllr)
        self.assertAlmostEqual(0.6952113122368764, calculate_cllr([1/100.]*100 + [100]*6, [1]).cllr)
        self.assertAlmostEqual(1.0000000000000000, calculate_cllr([1], [1]).cllr)
        self.assertAlmostEqual(1.0849625007211563, calculate_cllr([2], [2]*2).cllr)
        self.assertAlmostEqual(1.6699250014423126, calculate_cllr([8], [8]*8).cllr)

    def test_classifier_cllr(self):
        numpy.random.seed(0)
        clf = LogisticRegression()

        prev_cllr = 1
        for i in range(1, 10):
            X0 = numpy.random.normal(loc=[-1]*3, scale=.1, size=(i, 3))
            X1 = numpy.random.normal(loc=[1]*3, scale=.1, size=(i, 3))
            cllr = classifier_cllr(clf, X0, X1, X0, X1).cllr
            self.assertLess(cllr, prev_cllr)
            prev_cllr = cllr

        X0 = numpy.random.normal(loc=[-1]*3, size=(100, 3))
        X1 = numpy.random.normal(loc=[1]*3, size=(100, 3))
        self.assertAlmostEqual(0.1901544891867276, classifier_cllr(clf, X0, X1, X0, X1).cllr)

        X0 = numpy.random.normal(loc=[-.5]*3, size=(100, 3))
        X1 = numpy.random.normal(loc=[.5]*3, size=(100, 3))
        self.assertAlmostEqual(0.6153060581423102, classifier_cllr(clf, X0, X1, X0, X1).cllr)

        X0 = numpy.random.normal(loc=[0]*3, size=(100, 3))
        X1 = numpy.random.normal(loc=[0]*3, size=(100, 3))
        self.assertAlmostEqual(1.285423922204846, classifier_cllr(clf, X0, X1, X0, X1).cllr)

        X = numpy.random.normal(loc=[0]*3, size=(400, 3))
        self.assertAlmostEqual(1.3683601658310476, classifier_cllr(clf, X[:100], X[100:200], X[200:300], X[300:400]).cllr)


if __name__ == '__main__':
    unittest.main()