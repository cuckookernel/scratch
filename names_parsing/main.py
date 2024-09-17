# This is a sample Python script.

import random
import functools
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchtext
from torchtext.legacy import data
from torchtext.legacy.data import Dataset, Example

from transformers import BertTokenizer, BertModel
import numpy as np


SEED = 1234

# %%
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def _main():
    # %%
    _set_seeds()
    # %%
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    # %% init special tokenizer tokens
    init_token = tokenizer.cls_token
    pad_token = tokenizer.pad_token
    unk_token = tokenizer.unk_token

    print(init_token, pad_token, unk_token)

    init_token_idx = tokenizer.convert_tokens_to_ids(init_token)
    pad_token_idx = tokenizer.convert_tokens_to_ids(pad_token)
    unk_token_idx = tokenizer.convert_tokens_to_ids(unk_token)

    print(init_token_idx, pad_token_idx, unk_token_idx)
    # %%
    max_input_length = tokenizer.max_model_input_sizes['bert-base-uncased']

    print(max_input_length)
    # %%
    text_preprocessor = functools.partial(cut_and_convert_to_id,
                                          tokenizer=tokenizer,
                                          max_input_length=max_input_length)

    tag_preprocessor = functools.partial(cut_to_max_length,
                                         max_input_length=max_input_length)
    # %%
    TEXT = data.Field(use_vocab=False,
                      lower=True,
                      preprocessing=text_preprocessor,
                      init_token=init_token_idx,
                      pad_token=pad_token_idx,
                      unk_token=unk_token_idx)

    UD_TAGS = data.Field(unk_token=None,
                         init_token='<pad>',
                         preprocessing=tag_preprocessor)
    # %%
    examples = [ "tokens": ]
    # %%


def cut_to_max_length(tokens, max_input_length):
    tokens = tokens[:max_input_length - 1]
    return tokens


def cut_and_convert_to_id(tokens, tokenizer, max_input_length):
    tokens_trunc = tokens[:max_input_length-1]
    token_idxs = tokenizer.convert_tokens_to_ids(tokens_trunc)
    return token_idxs


def _set_seeds():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.backends.cudnn.deterministic = True
    # %%
