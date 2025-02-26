# Детектор состояния человека - репозиторий команды `LaboRad`

С 13 февраля 2025 года документация находится на сайте https://tphlru.github.io/

Основной графический интерфейс находиться в gui/laborad_detector

Для работы требуется Python = 3.9.*

### Установка библиотек

```
conda env create -f /home/timur/Projects/rzd_detector2/environment.yaml
conda activate ti2
pip install -r reqs.txt
pip install poetry cython
poetry lock
poetry install
```

```bash
pip install -r ../requirements.txt
conda install compilers libstdcxx-ng=12
conda install webrtcvad
```

### Для публикации:
```
poetry lock
poetry install
poetry publish --build
```

### Known Errors Fixes

Loaded runtime CuDNN library: 8.2.1 but source was compiled with: 8.9.6.  CuDNN library needs to have matching major version and equal or higher minor version. If using a binary install, upgrade your CuDNN library.  If building from sources, make sure the library loaded at runtime is compatible with the version specified during compile configuration.

Нужно обновить CuDNN до версии 8.9.*

```bash
# pip index versions nvidia-cudnn-cu12
pip install --upgrade nvidia-cudnn-cu12==8.9.*
conda uninstall cudnn
```

OSError: libtorch_cuda_cpp.so: cannot open shared object file: No such file or directory

```bash
conda install pytorch=2.3.1=py3.9_cuda12.*_cudnn8.9.* torchvision torchaudio -c pytorch -c nvidia
```

fatal error: crypt.h: No such file or directory #include <crypt.h>
error: command '/home/timur/miniforge3/envs/ti/bin/x86_64-conda-linux-gnu-cc' failed with exit code 1

Нужно установить libxcrypt через conda (https://github.com/stanford-futuredata/ColBERT/issues/309)
```bash
conda install --channel=conda-forge libxcrypt
export CPATH=/opt/conda/include/     
```

ModuleNotFoundError: No module named '_sysconfigdata_x86_64_conda_cos7_linux_gnu'
conda install python=3.9.7 pip --force-reinstall
cd $(python -c "import sys; print(sys.prefix)")/lib/python3.9
ln -s _sysconfigdata_x86_64_conda_linux_gnu.py _sysconfigdata_x86_64_conda_cos7_linux_gnu.py


Error while loading conda entry point: conda-libmamba-solver (/home/timur/.conda/envs/ti/lib/libstdc++.so.6: version `GLIBCXX_3.4.32' not found (required by /usr/lib64/python3.13/site-packages/libmambapy/bindings.cpython-313-x86_64-linux-gnu.so))


conda install --solver=classic conda-forge::conda-libmamba-solver conda-forge::libmamba conda-forge::libmambapy conda-forge::libarchive
conda install -c conda-forge libstdcxx-ng

Unrecognized option 'preset'.
Error splitting the argument list: Option not found

conda install -c conda-forge ffmpeg

TEMP:
```
sudo dnf -y install cuda-toolkit-12-5
conda install -c conda-forge cudatoolkit cudnn

echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh

pip install tensorflow[and-cuda]

# Verify install:
python3 -c "import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'; import tensorflow as tf; print('Num GPUs Available: ', len(tf.config.list_physical_devices('GPU')))"
```

Run web server:
`cd gui/dev/web-server/ && gunicorn -w 4 'webserver:app' -b 0.0.0.0:46578`

Также мы используем poetry и https://poethepoet.natn.io/poetry_plugin.html#hooking-into-poetry-commands

Все права защищены. Копирование и частичное использование строго запрещено. Только для образовательных целей.
All rights reserved. Copying and partial use is strictly prohibited. For educational purposes only.
