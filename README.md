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

Все права защищены. Копирование и частичное использование строго запрещено. Только для образовательных целей. All rights reserved. Copying and partial use is strictly prohibited. For educational purposes only.