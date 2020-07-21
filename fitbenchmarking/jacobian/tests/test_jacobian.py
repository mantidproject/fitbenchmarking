
from collections import OrderedDict
from unittest import TestCase

import numpy as np

from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils import exceptions
from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.jacobian.SciPyFD_3point_jacobian import ScipyThreePoint
from fitbenchmarking.jacobian.SciPyFD_cs_jacobian import ScipyCS
from fitbenchmarking.jacobian.analytic_jacobian import Analytic
from fitbenchmarking.jacobian.jacobian_factory import create_jacobian


def f(x, p1, p2):
    """
    Test function for numerical Jacobians

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p1: parameter 1
    :type p1: float
    :param p2: parameter 1
    :type p2: float

    :return: function evaluation
    :rtype: numpy array
    """
    return p1 * np.exp(p2 * x)


def J(x, p):
    """
    Analytic Jacobian evaluation

    :param x: x data points, defaults to self.data_x
    :type x: numpy array, optional
    :param p: list of parameters to fit
    :type p: list

    :return: Jacobian evaluation
    :rtype: numpy array
    """
    return np.column_stack((-np.exp(p[1] * x),
                            -x * p[0] * np.exp(p[1] * x)))


class TestJacobianClass(TestCase):
    """
    Tests for Jacobian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        options.use_errors = False
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f
        self.fitting_problem.jacobian = J
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.params = [6, 0.1]
        self.actual = J(x=self.fitting_problem.data_x, p=self.params)

    def test_scipy_two_point_eval(self):
        """
        Test for ScipyTwoPoint evaluation is correct
        """
        jac = ScipyTwoPoint(self.fitting_problem)
        eval_result = jac.eval(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_scipy_three_point_eval(self):
        """
        Test for ScipyThreePoint evaluation is correct
        """
        jac = ScipyThreePoint(self.fitting_problem)
        eval_result = jac.eval(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_scipy_cs_eval(self):
        """
        Test for ScipyCS evaluation is correct
        """
        jac = ScipyCS(self.fitting_problem)
        eval_result = jac.eval(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_analytic_cutest_no_errors(self):
        """
        Test analytic jacobian
        """
        self.fitting_problem.format = "cutest"
        jac = Analytic(self.fitting_problem)
        eval_result = jac.eval(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_analytic_cutest_errors(self):
        """
        Test analytic jacobian
        """
        self.fitting_problem.options.use_errors = True
        e = np.array([1, 2, 1, 3, 1])
        self.fitting_problem.data_e = e
        self.fitting_problem.format = "cutest"
        jac = Analytic(self.fitting_problem)
        eval_result = jac.eval(params=self.params)
        scaled_actual = self.actual / e[:, None]
        self.assertTrue(np.isclose(scaled_actual, eval_result).all())


class TestCachedFuncValues(TestCase):
    """
    Tests for Jacobian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        options.use_errors = False
        self.fitting_problem = FittingProblem(options)
        self.jacobian = Jacobian(self.fitting_problem)

    def func(self, x):
        """
        Test function for cached value tests.

        :param x: parameters to evaluate function at
        :type x: numpy array

        :return: function evaluation
        :rtype: float
        """
        return x[0] * x[1] + x[2]**2

    def test_check_cached_eval(self):
        """
        Checks cached function values
        """
        params = [1, 2, 4]
        expected_value = self.func(params)
        cached_dict = {"params": params, "value": expected_value}
        computed_value = self.jacobian.cached_func_values(cached_dict,
                                                          self.func,
                                                          params)
        assert expected_value == computed_value

    def test_check_none_cached_eval(self):
        """
        Checks function values
        """
        params = [1, 2, 3]
        expected_value = self.func(params)
        cached_dict = {"params": [1, 2, 4], "value": 18}
        computed_value = self.jacobian.cached_func_values(cached_dict,
                                                          self.func,
                                                          params)
        assert expected_value == computed_value


class TestDerivCostFunc(TestCase):
    """
    Tests for Jacobian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        options.use_errors = False
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.function = f
        self.fitting_problem.jacobian = J
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.params = [6, 0.1]
        J_eval = J(x=self.fitting_problem.data_x,
                   p=self.params)
        f_eval = f(x=self.fitting_problem.data_x,
                   p1=self.params[0],
                   p2=self.params[1])
        self.actual = np.matmul(J_eval.T, f_eval)

    def test_scipy_two_point_eval(self):
        """
        Test for ScipyTwoPoint evaluation is correct
        """
        jac = ScipyTwoPoint(self.fitting_problem)
        self.fitting_problem.jac = jac
        eval_result = jac.eval_r_norm(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_scipy_three_point_eval(self):
        """
        Test for ScipyThreePoint evaluation is correct
        """
        jac = ScipyThreePoint(self.fitting_problem)
        self.fitting_problem.jac = jac
        eval_result = jac.eval_r_norm(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_scipy_cs_point_eval(self):
        """
        Test for ScipyCS evaluation is correct
        """
        jac = ScipyCS(self.fitting_problem)
        self.fitting_problem.jac = jac
        eval_result = jac.eval_r_norm(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())

    def test_analytic_cutest(self):
        """
        Test analytic jacobian
        """
        self.fitting_problem.format = "cutest"
        jac = Analytic(self.fitting_problem)
        self.fitting_problem.jac = jac
        eval_result = jac.eval_r_norm(params=self.params)
        self.assertTrue(np.isclose(self.actual, eval_result).all())


class FactoryTests(TestCase):
    """
    Tests for the Jacobian factory
    """

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """
        self.options = Options()

        valid = ['2point', '3point', 'cs']
        expected_name = ["scipytwopoint", "scipythreepoint", "scipycs"]

        invalid = ['foo', 'bar', 'hello', 'r2d2']

        for v, e in zip(valid, expected_name):
            self.options.num_method = v
            jac = create_jacobian(self.options)
            self.assertTrue(jac.__name__.lower().startswith(e))

        for i in invalid:
            self.options.num_method = i
            self.assertRaises(exceptions.NoJacobianError,
                              create_jacobian,
                              self.options)
