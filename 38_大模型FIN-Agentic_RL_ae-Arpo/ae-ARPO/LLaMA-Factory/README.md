# LLaMA Factory - Easy & Efficient LLM Fine-Tuning

LLaMA Factory is a unified framework for efficient fine-tuning of large language models, used here as the cold-start SFT stage for AEARPO/ARAEPO training.

## Key Features

- Full-parameter fine-tuning, LoRA, QLoRA, and other efficient tuning methods
- Supports Qwen, Llama, and other popular model families
- Integrated with DeepSpeed for distributed training
- Web UI for easy management

## Usage (in this project)

```bash
cd LLaMA-Factory
conda create -n sft python=3.10
conda activate sft
pip install -r requirements.txt
bash aearpo_train_sft/sft_train.sh
```
