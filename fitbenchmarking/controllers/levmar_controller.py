""" 
Implements a controller for the levmar fitting software.
http://www.ics.forth.gr/~lourakis/levmar/
via the python interface
https://pypi.org/project/levmar/
"""

import levmar

from fitbenchmarking.controllers.base_controller import Controller

class LevmarController(Controller):
    """
    Controller for the levmar fitting software
    """

    def __init__(self, cost_func):
        """
        Initialise the class.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super(LevmarController, self).__init__(cost_func)
        self._popt = None
        self.algorithm_check = {
            'all': ['levmar', 'levmar-no-jac'],
            'ls': ['levmar', 'levmar-no-jac'],
            'deriv_free': [None],
            'general': [None]}

    def jacobian_information(self):
        """ 
        levmar can use Jacobian information
        """
        has_jacobian = True
        jacobian_free_solvers = ["levmar-no-jac"]
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup problem ready to be run with levmar
        """

        return

    def _feval(self, p, x):
        """
        Utility function to call problem.eval_model with correct args

        :param p: parameters
        :type p: list
        :param data: x data
        :type data: list
        :return: result from problem.eval_model
        :rtype: numpy array
        """
        
        fx = self.problem.function(self.data_x, *p) #(eval_model(params=p)
        return fx

    def _jeval(self, p, x):
        """
        Utility function to call jac.eval with correct args

        :param p: parameters
        :type p: list
        :param data: x data, this is discarded as the defaults can be used.
        :type data: N/A
        :return: result from jac.eval
        :rtype: numpy array
        """
        jac = -self.jacobian.eval(p)
        return jac

    def fit(self):
        """
        run problem with levmar
        """
        if self.minimizer == "levmar-no-jac":
            jac = None
        else:
            jac = self._jeval

        (self.final_params, cov, self._info) = levmar.levmar(self._feval,
                                                        self.initial_params,
                                                        self.data_y,
                                                        args=(self.data_x,),
                                                        jacf=jac)
        # self._info isn't documented (other than in the levmar source),
        # but returns:
        # self._info[0] = ||e||_2 at `p0`
        # self._info[1] = ( ||e||_2 at `p`
        #                   ||J^T.e||_inf
        #                   ||Dp||_2
        #                   mu / max[J^T.J]_ii),
        # self._info[2] = number of iterations
        # self._info[3] = reason for terminating (as a string)
        # self._info[4] = number of `func` evaluations
        # self._info[5] = number of `jacf` evaluations
        # self._info[6] = number of linear system solved
        

    def cleanup(self):
        """ 
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        
        if self._info[3] == "Stop by small Dp":
            self.flag = 0
        elif self._info[3] == "Stopped by small gradient J^T e":
            self.flag = 0
        elif self._info[3] == "Stopped by small ||e||_2":
            self.flag = 0
        elif self._info[3] == "maxit":
            self.flag = 1
        else:
            self.flag = 2

