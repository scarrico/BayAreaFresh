# Version controlled here because installing OpenCV is truely a PIA.
# Thanks: https://medium.com/@nszceta/python-3-6-opencv-3-2-and-pyenv-on-macos-sierra-6ebcebd6193e
# Use this to get different versions of python to run nicely in a virtual environment.
# To test this worked execute:
#   python -c "import cv2; print(cv2.__version__)"
#
# HINT: If things aren't working right, check ~/.bashrc and ~/.bash_profile
# Those files had better not be initializing a virtual environment besides pyenv
# There needs to be a like like:
#   if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi
# If not, add it.  If you added that line, then you need to 
# . ~/bash_profile   # or the file you edited
# Then re-run this script.  If this script doesn't complete properly, you 
# probably need to dot execute the bash_profile again and then run the script.
# Expect to run this script at least twice if not three times until it is complete

#!/usr/bin/env bash
set -o errexit

function run () {
# step 1. install brew (http://brew.sh)
if ! type "brew" > /dev/null; then
  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi
brew cleanup
brew update
brew upgrade
brew tap homebrew/science
brew install eigen tbb hdf5 tesseract \
    libjpeg-turbo libtiff libpng pyenv-virtualenv

# step 2. set up pyenv
if ! type "pyenv" > /dev/null; then
  echo "error: pyenv not installed properly"
  echo "info: install pyenv"
  exit 1
fi

env PYTHON_CONFIGURE_OPTS="--enable-shared" CFLAGS="-O2" pyenv install 3.6.0
pyenv global 3.6.0

if [[ `python --version` != "Python 3.6.0" ]]; then
  echo "error: python installation failure"
  echo "info: check if pyenv is installed correctly"
  echo `python --version`
  exit 1
fi

if [[ `which python` != "${HOME}/.pyenv/shims/python" ]]; then
  echo "error: failed to detect pyenv python"
  echo "info: check if pyenv is installed correctly"
  exit 1
fi

# step 3. install numpy
pip install -U pip setuptools wheel cython numpy

# step 4. build opencv
sudo mkdir -p /opt/src
sudo chown $(whoami):staff /opt
sudo chown $(whoami):staff /opt/src
cd /opt/src
curl -L https://github.com/opencv/opencv/archive/3.2.0.zip -o opencv32.zip
curl -L https://github.com/opencv/opencv_contrib/archive/3.2.0.zip -o opencv32contrib.zip
unzip opencv32.zip
unzip opencv32contrib.zip
mv -v opencv-3.2.0 /opt/src/opencv32_py36
mv -v opencv_contrib-3.2.0 /opt/src/opencv32_py36_contrib
cd /opt/src/opencv32_py36
mkdir /opt/src/opencv32_py36/release
cd /opt/src/opencv32_py36/release
cmake \
    -D CMAKE_INSTALL_PREFIX=/opt/opencv32_py36 \
    -D OPENCV_EXTRA_MODULES_PATH=/opt/src/opencv32_py36_contrib/modules \
    -D BUILD_opencv_python2=OFF \
    -D BUILD_opencv_python3=ON \
    -D BUILD_TIFF=ON \
    -D BUILD_opencv_java=OFF \
    -D WITH_CUDA=OFF \
    -D ENABLE_FAST_MATH=1 \
    -D ENABLE_AVX=ON \
    -D WITH_OPENGL=ON \
    -D WITH_OPENCL=ON \
    -D WITH_IPP=OFF \
    -D WITH_TBB=ON \
    -D WITH_EIGEN=ON \
    -D WITH_V4L=OFF \
    -D WITH_VTK=OFF \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D PYTHON3_LIBRARY=$(python -c "import re, os.path; print(os.path.normpath(os.path.join(os.path.dirname(re.__file__), '..', 'libpython3.6m.dylib')))") \
    -D PYTHON3_EXECUTABLE=$(which python) \
    -D PYTHON3_INCLUDE_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
    -D PYTHON3_PACKAGES_PATH=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") ..
    make -j8
    make install
    # Installing: /Users/adamgradzki/.pyenv/versions/3.6.0/lib/python3.6/site-packages/cv2.cpython-36m-darwin.so

    pyenv virtualenv 3.6.0 main
    pyenv global main
    pip install -U pip setuptools wheel numpy
    ln -s "$HOME/.pyenv/versions/3.6.0/lib/python3.6/site-packages/cv2.cpython-36m-darwin.so" \
        "$HOME/.pyenv/versions/main/lib/python3.6/site-packages/cv2.cpython-36m-darwin.so"
}
run
