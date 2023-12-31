# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_model.ipynb.

# %% auto 0
__all__ = ["ImageEncoder", "TextEncoder", "ProjectionHead", "CLIP", "cross_entropy"]

# %% ../nbs/03_model.ipynb 3
from torch_snippets import *
from .core import *

# %% ../nbs/03_model.ipynb 4
import timm
from transformers import DistilBertModel, DistilBertConfig


# %% ../nbs/03_model.ipynb 5
class ImageEncoder(nn.Module):
    """
    Encode images to a fixed size vector
    """

    def __init__(self, config):
        super().__init__()
        self.model = timm.create_model(
            config.model_name, config.pretrained, num_classes=0, global_pool="avg"
        )
        for p in self.model.parameters():
            p.requires_grad = config.trainable

    def forward(self, x):
        return self.model(x)


class TextEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        if config.pretrained:
            self.model = DistilBertModel.from_pretrained(
                config.distilbert_text_encoder_model
            )
        else:
            self.model = DistilBertModel(config=DistilBertConfig())
        for p in self.model.parameters():
            p.requires_grad = config.trainable
        self.target_token_idx = config.target_token_idx

    def forward(self, input_ids, attention_mask):
        output = self.model(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = output.last_hidden_state
        return last_hidden_state[:, self.target_token_idx, :]


class ProjectionHead(nn.Module):
    def __init__(self, embedding_dim, config):
        super().__init__()
        self.projection = nn.Linear(embedding_dim, config.projection_dim)
        self.gelu = nn.GELU()
        self.fc = nn.Linear(config.projection_dim, config.projection_dim)
        self.dropout = nn.Dropout(config.dropout)
        self.layer_norm = nn.LayerNorm(config.projection_dim)

    def forward(self, x):
        projected = self.projection(x)
        x = self.gelu(projected)
        x = self.fc(x)
        x = self.dropout(x)
        x = x + projected
        x = self.layer_norm(x)
        return x


class CLIP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.image_encoder = ImageEncoder(config)
        self.text_encoder = TextEncoder(config)
        self.image_projection = ProjectionHead(config.image_embedding, config)
        self.text_projection = ProjectionHead(config.text_embedding, config)
        self.temperature = config.temperature

    def forward(self, image, input_ids, attention_mask):
        # Getting Image and Text Features
        image_features = self.image_encoder(image)
        text_features = self.text_encoder(
            input_ids=input_ids, attention_mask=attention_mask
        )
        # Getting Image and Text Embeddings (with same dimension)
        image_embeddings = self.image_projection(image_features)
        text_embeddings = self.text_projection(text_features)
        # Calculating the Loss
        logits = (text_embeddings @ image_embeddings.T) / self.temperature
        images_similarity = image_embeddings @ image_embeddings.T
        texts_similarity = text_embeddings @ text_embeddings.T
        targets = F.softmax(
            (images_similarity + texts_similarity) / 2 * self.temperature, dim=-1
        )
        texts_loss = cross_entropy(logits, targets, reduction="none")
        images_loss = cross_entropy(logits.T, targets.T, reduction="none")
        loss = (images_loss + texts_loss) / 2.0  # shape: (batch_size)
        return {"loss": loss.mean()}

    @classmethod
    def from_pretrained(cls, folder, config):
        model = cls(config)
        load_torch_model_weights_to(model, P(folder) / "pytorch_model.bin")
        return model


def cross_entropy(preds, targets, reduction="none"):
    log_softmax = nn.LogSoftmax(dim=-1)
    loss = (-targets * log_softmax(preds)).sum(1)
    if reduction == "none":
        return loss
    elif reduction == "mean":
        return loss.mean()
