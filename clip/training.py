# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_train.ipynb.

# %% auto 0
__all__ = []

# %% ../nbs/04_train.ipynb 3
import itertools
from torch_snippets import *
from torch_snippets.imgaug_loader import iaa

from .core import *
from .config import ClipConfig
from .dataset import build_clip_data_loaders
from .models import CLIP
