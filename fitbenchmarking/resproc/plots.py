"""
Higher level functions that are used for plotting the best fit plot and a starting guess plot.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from fitbenchmarking.utils import create_dirs


class plot(object):
    """
    Class providing plotting functionality.
    """

    def __init__(self, problem, options, count, group_results_dir):
        self.problem = problem
        self.options = options
        self.count = count
        self.group_results_dir = group_results_dir
        self.figures_dir = create_dirs.figures(group_results_dir)

    def default_plot_options(self):
        """
        Defines defaults plot options for matplotlib
        """
        self.markers = "x"
        self.colour = "k"
        self.linestyle = '--'
        self.z_order = 2
        self.linewidth = 1.5
        self.legend_location = "upper left"
        self.title_size = 10

    def format_plot(self):
        """
        Performs post plot processing to annotate the plot correctly
        """
        plt.xlabel("Time ($\mu s$)")
        plt.ylabel("Arbitrary units")
        plt.title(self.problem.name + " " + str(self.count),
                  fontsize=self.title_size)
        plt.legend(labels=self.labels, loc=self.legend_location)
        plt.tight_layout()

    def plot_data(self, errors, x=None, y=None):
        """
        Plots the data given
        """
        if x is None:
            x = self.problem.data_x
        if y is None:
            y = self.problem.data_y
        if errors:
            # Plot with errors
            plt.errorbar(x, y,
                         yerr=self.problem.data_e,
                         marker=self.markers, color=self.colour,
                         linestyle=self.linestyle, markersize=8,
                         zorder=self.z_order, linewidth=self.linewidth)
        else:
                # Plot without errors
            plt.plot(x, y,
                     marker=self.markers, color=self.colour,
                     linestyle=self.linestyle, markersize=8,
                     zorder=self.z_order, linewidth=self.linewidth)

    def plot_initial_guess(self):
        """
        Plots the initial guess along with the data
        """
        self.default_plot_options()
        self.labels = ["Starting Guess", "Data"]
        self.plot_data(self.options.use_errors)

        ini_guess = self.problem.starting_values[self.count - 1].values()
        self.colour = "red"
        self.markers = ""
        self.linestyle = '-'
        self.linewidth = 2
        y = self.problem.eval_f(ini_guess)
        self.plot_data(False, y=y)
        self.format_plot()
        file_name = "{0}/start_for_{1}_{2}.png".format(
            self.figures_dir, self.problem.name, self.count)
        plt.savefig(file_name)
        plt.close()

    def plot_best_fit(self, best_fit):
        """
        Plots the best fit along with the data
        """
        self.default_plot_options()
        self.labels = [best_fit['name'], "Data"]
        self.plot_data(self.options.use_errors)
        self.colour = "lime"
        self.markers = ""
        self.linestyle = '-'
        self.linewidth = 2
        self.plot_data(False, y=self.problem.eval_f(best_fit['value']))
        self.format_plot()
        file_name = "{0}/Fit_for_{1}_{2}.png".format(
            self.figures_dir, self.problem.name, self.count)
        plt.savefig(file_name)
        plt.close()
