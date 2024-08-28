# Детектор состояния человека - репозиторий команды `[laborad]`

pip install -e .

```bash
pip install -r ../requirements.txt
conda install compilers libstdcxx-ng=12
conda install webrtcvad
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


TEMP:
```
sudo dnf -y install cuda-toolkit-12-5
conda install -c conda-forge cudatoolkit cudnn

echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh

pip install tensorflow[and-cuda]

# Verify install:
python3 -c "import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'; import tensorflow as tf; print('Num GPUs Available: ', len(tf.config.list_physical_devices('GPU')))"
```

Все права защищены. Копирование и частичное использование строго запрещено. Только для образовательных целей. All rights reserved. Copying and partial use is strictly prohibited. For educational purposes only.