# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_config.ipynb.

# %% auto 0
__all__ = ["ClipConfig"]

# %% ../nbs/01_config.ipynb 3
from .core import *
from torch_snippets import *


# %% ../nbs/01_config.ipynb 4
class ClipConfig:
    debug = False
    batch_size = 32
    num_workers = 2
    head_lr = 1e-3
    image_encoder_lr = 1e-4
    text_encoder_lr = 1e-5
    weight_decay = 1e-3
    patience = 1
    factor = 0.8
    epochs = 4
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "resnet50"
    image_embedding = 2048
    distilbert_text_encoder_model = "distilbert-base-uncased"
    text_embedding = 768
    distilbert_text_tokenizer = "distilbert-base-uncased"
    max_length = 200
    pretrained = trainable = True  # for both image encoder and text encoder
    temperature = 1.0
    # image size
    size = 224
    # for projection head; used for both image and text encoders
    num_projection_layers = 1
    projection_dim = 256
    dropout = 0.1
    target_token_idx = 0
    save_eval_and_logging_steps = 500
