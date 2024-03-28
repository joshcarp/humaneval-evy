---
license: bigcode-openrail-m
library_name: peft
tags:
- generated_from_trainer
base_model: bigcode/starcoder2-3b
model-index:
- name: results
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# results

This model is a fine-tuned version of [bigcode/starcoder2-3b](https://huggingface.co/bigcode/starcoder2-3b) on an unknown dataset.
It achieves the following results on the evaluation set:
- Loss: 1.3846

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 5e-05
- train_batch_size: 4
- eval_batch_size: 16
- seed: 42
- gradient_accumulation_steps: 4
- total_train_batch_size: 16
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 3

### Training results

| Training Loss | Epoch | Step | Validation Loss |
|:-------------:|:-----:|:----:|:---------------:|
| No log        | 1.0   | 1    | 1.3867          |
| No log        | 2.0   | 3    | 1.3846          |


### Framework versions

- PEFT 0.10.1.dev0
- Transformers 4.40.0.dev0
- Pytorch 2.2.1
- Datasets 2.18.1.dev0
- Tokenizers 0.15.2