# Use the basic dependencies
FROM fitbenchmarking/fitbenchmarking-deps:latest

WORKDIR /

#################
# Install pygsl #
#################

RUN apt-get update && \
 apt-get install -y gsl-bin \
 libgsl-dev \
 libgsl-dbg

##################
# Install RALFit #
##################
RUN apt-get install -y gfortran \
    lcov \
    libblas-dev \
    liblapack-dev \
    libgdal-dev

RUN git clone https://github.com/ralna/RALFit

RUN pip install numpy

RUN mkdir -p /RALFit/libRALFit/build

WORKDIR /RALFit/libRALFit/build

RUN cmake .. && make && make install

# make install for RALFit doesn't work on docker, so manually pip install
RUN pip install .

ENV LD_LIBRARY_PATH=/RALFit/libRALFit/build/src:$LD_LIBRARY_PATH

################
# Build cutest #
################

RUN mkdir -p /cutest

WORKDIR /cutest

RUN git clone https://github.com/ralna/ARCHDefs ./archdefs && \
    git clone https://github.com/ralna/SIFDecode ./sifdecode && \
    git clone https://github.com/ralna/CUTEst ./cutest

RUN mkdir pycutest_cache

ENV ARCHDEFS=/cutest/archdefs/ \
    SIFDECODE=/cutest/sifdecode/ \
    MASTSIF=/home/fitbenchmarking/examples/benchmark_problems/SIF/ \
    CUTEST=/cutest/cutest/ \
    MYARCH="pc64.lnx.gfo" \
    PYCUTEST_CACHE=/cutest/pycutest_cache/

ENV PYTHONPATH="${PYCUTEST_CACHE}:${PYTHONPATH}"

# Install sifdecode

WORKDIR $SIFDECODE
RUN printf "6\n2\n6\n" > sifdecode.input && \
    printf "nny" >> sifdecode.input && \
    ./install_sifdecode  < sifdecode.input

# Install cutest
WORKDIR $CUTEST
RUN printf "6\n2\n6\n2\n8\n" > cutest.input && \
    printf "nnydn" >> cutest.input && \
    ./install_cutest < cutest.input

# install pycutest
RUN python -m pip install pycutest

##################
# Install Mantid #
##################

WORKDIR /
# set noninteractive to stop tzdata prompt
ENV DEBIAN_FRONTEND=noniteractive
ENV VIRTUAL_ENV=""
ENV OLD_PATH=$PATH
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN apt-get install -y git g++ qt5-default clang-format-6.0 cmake dvipng doxygen libtbb-dev \
  libgoogle-perftools-dev libboost-all-dev libpoco-dev libnexus-dev libhdf5-dev libhdf4-dev \
  libjemalloc-dev libgsl-dev liboce-visualization-dev libmuparser-dev libssl-dev libjsoncpp-dev \
  librdkafka-dev qtbase5-dev qttools5-dev qttools5-dev-tools libqt5webkit5-dev \
  libqt5x11extras5-dev libqt5opengl5-dev libqscintilla2-qt5-dev libpython3-dev \
  ninja-build python3-setuptools python3-sip-dev python3-pyqt5 pyqt5-dev pyqt5-dev-tools \
  python3-qtpy python3-numpy python3-scipy python3-sphinx python3-sphinx-bootstrap-theme \
  python3-pycifrw python3-dateutil python3-matplotlib python3-qtconsole python3-h5py \
  python3-mock python3-psutil python3-requests python3-toml python3-yaml wget

# Details from mantid website
RUN wget https://downloads.sourceforge.net/project/mantid/6.0/mantid-6.0.0-Source.tar.xz
RUN tar -xvf mantid-6.0.0-Source.tar.xz
RUN rm mantid*.xz

RUN apt-get install -y ccache
RUN ccache --max-size=20G

RUN mkdir -p /opt/Mantid

WORKDIR /opt/Mantid
RUN cmake /mantid-6.0.0-Source -DENABLE_MANTIDPLOT=OFF
RUN make

ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$OLD_PATH
RUN unset OLD_PATH
ENV PYTHONPATH=$PYTHONPATH:/opt/Mantid/lib:/opt/Mantid/bin
RUN python -m pip install IPython six python-dateutil pyyaml h5py
ENV HDF5_DISABLE_VERSION_CHECK=2
RUN /opt/Mantid/bin/mantidpython -m  mantid.simpleapi || echo "expected segfault on first run"

WORKDIR /

#################
# install pygsl #
#################
RUN python -m pip install pygsl


## ALL SET UP ##
WORKDIR /home/
