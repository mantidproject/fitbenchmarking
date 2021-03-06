"""
Implements a controller for the CERN pacakage Minuit
https://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/
using the iminuit python interface
http://iminuit.readthedocs.org
"""
from iminuit import Minuit
from iminuit import __version__ as iminuit_version
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingSoftwareError


class MinuitController(Controller):
    """
    Controller for the Minuit fitting software
    """

    def __init__(self, cost_func):
        """
        Initializes variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """

        if int(iminuit_version[:1]) < 2:
            raise MissingSoftwareError('iminuit version {} is not supported, '
                                       'please upgrade to at least version '
                                       '2.0.0'.format(iminuit_version))

        super(MinuitController, self).__init__(cost_func)
        self._popt = None
        self._initial_step = None
        self._minuit_problem = None
        self.algorithm_check = {
            'all': ['minuit'],
            'ls': [None],
            'deriv_free': [None],
            'general': ['minuit']}

    def jacobian_information(self):
        """
        Minuit cannot use Jacobian information
        """
        has_jacobian = False
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup for Minuit
        """
        # minuit requires an initial step size.
        # The docs say
        # "A good guess is a fraction of the initial
        #  fit parameter value, e.g. 10%
        #  (be careful when applying this rule-of-thumb
        #  when the initial parameter value is zero "
        self._initial_step = 0.1 * np.array(self.initial_params)
        # set small steps to something sensible(?)
        self._initial_step[self._initial_step < 1e-12] = 1e-12
        self._minuit_problem = Minuit(self.cost_func.eval_cost,
                                      self.initial_params)
        self._minuit_problem.errordef = 1
        self._minuit_problem.errors = self._initial_step

    def fit(self):
        """
        Run problem with Minuit
        """
        self._minuit_problem.migrad()  # run optimizer
        self._status = 0 if self._minuit_problem.valid else 1

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        fmin = self._minuit_problem.fmin
        if self._status == 0:
            self.flag = 0
        elif fmin.has_reached_call_limit:
            self.flag = 1
        else:
            self.flag = 2

        self._popt = np.array(self._minuit_problem.values)
        self.final_params = self._popt
