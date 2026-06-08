# verl: Reinforcement Learning for LLMs

verl is a flexible, efficient and production-ready RL training library for large language models (LLMs).

verl is flexible and easy to use with:

- **Easy extension of diverse RL algorithms**: The hybrid-controller programming model enables flexible representation and efficient execution of complex post-training dataflows. Build RL dataflows such as GRPO, PPO in a few lines of code.

- **Seamless integration of existing LLM infra with modular APIs**: Decouples computation and data dependencies, enabling seamless integration with existing LLM frameworks, such as FSDP, Megatron-LM, vLLM, SGLang, etc

- **Flexible device mapping**: Supports various placement of models onto different sets of GPUs for efficient resource utilization and scalability across different cluster sizes.

- Ready integration with popular HuggingFace models

verl is fast with:

- **State-of-the-art throughput**: SOTA LLM training and inference engine integrations and SOTA RL throughput.

- **Efficient actor model resharding with 3D-HybridEngine**: Eliminates memory redundancy and significantly reduces communication overhead during transitions between training and generation phases.

## Key Features

- **FSDP**, **FSDP2** and **Megatron-LM** for training.
- **vLLM**, **SGLang** and **HF Transformers** for rollout generation.
- Compatible with Hugging Face Transformers and Modelscope Hub: Qwen-3, Qwen-2.5, Llama3.1, Gemma2, DeepSeek-LLM, etc
- Supervised fine-tuning.
- Reinforcement learning with PPO, GRPO, ReMax, REINFORCE++, RLOO, PRIME, DAPO, DrGRPO, etc.
  - Support model-based reward and function-based reward (verifiable reward) for math, coding, etc
  - Support vision-language models (VLMs) and multi-modal RL
  - Multi-turn with tool calling
- LLM alignment recipes such as Self-play preference optimization (SPPO)
- Flash attention 2, sequence packing, sequence parallelism support via DeepSpeed Ulysses, LoRA, Liger-kernel.
- Scales up to 70B models and hundreds of GPUs.
- Multi-gpu LoRA RL support to save memory.
- Experiment tracking with wandb, swanlab, mlflow and tensorboard.

## Getting Started

**Quickstart:**

- Installation
- Quickstart
- Programming Guide
- PPO in verl
- GRPO in verl

**Running a PPO example step-by-step:**

- Data and Reward Preparation
  - Prepare Data for Post-Training
  - Implement Reward Function for Dataset
- Understanding the PPO Example
  - PPO Example Architecture
  - Config Explanation

**Reproducible algorithm baselines:**

- RL performance on coding, math

**For code explanation and advance usage (extension):**

- PPO Trainer and Workers
  - PPO Ray Trainer
  - PyTorch FSDP Backend
  - Megatron-LM Backend
- Advance Usage and Extension
  - Multi-turn Rollout Support
  - Ray API design tutorial
  - Extend to Other RL(HF) algorithms
  - Add Models with the FSDP Backend
  - Add Models with the Megatron-LM Backend
  - Deployment using Separate GPU Resources

## Performance Tuning Guide

The performance is essential for on-policy RL algorithm. Refer to the performance tuning guide to optimize performance.

## Upgrade to vLLM >= v0.8.2

verl supports vLLM>=0.8.2 when using FSDP as the training backend. Please avoid vllm 0.7.x, which contains bugs that may lead to OOMs and unexpected errors.

## Use Latest SGLang

SGLang is fully supported with verl, with unique features including multi-turn agentic RL, VLM RLHF, server-based RL, and partial rollout.

## Upgrade to FSDP2

verl fully supports FSDP2! To enable FSDP2, set the following options:
```
actor_rollout_ref.ref.strategy=fsdp2
actor_rollout_ref.actor.strategy=fsdp2
critic.strategy=fsdp2
reward_model.strategy=fsdp2
```

## AMD Support (ROCm Kernel)

verl supports FSDP as the training engine (Megatron support coming soon) and integrates with vLLM and SGLang as inference engines.
