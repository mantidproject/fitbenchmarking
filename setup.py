from setuptools import setup, find_packages

from build.commands.install import InstallExternals
setup(name='FitBenchmarking',
      version='1.0',
      description='Fit benchmarking software',
      author='ISIS Fit Benchmarking Team',
      url='http://github.com/mantidproject/fitbenchmarking',
      license='GPL-3.0',
      packages=find_packages(),
      install_requires=['docutils'],
      zip_safe=False,
      cmdclass={
          'externals': InstallExternals,
      },
     )
