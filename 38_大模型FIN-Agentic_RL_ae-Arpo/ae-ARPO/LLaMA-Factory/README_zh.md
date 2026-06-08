# LLaMA Factory - 高效 LLM 微调框架

LLaMA Factory 是一个统一的大语言模型高效微调框架，在此项目中用作 AEARPO/ARAEPO 训练的冷启动 SFT 阶段。

## 主要特性

- 全参数微调、LoRA、QLoRA 等高效微调方法
- 支持 Qwen、Llama 等主流模型系列
- 集成 DeepSpeed 分布式训练
- Web UI 管理界面

## 使用方式

```bash
cd LLaMA-Factory
conda create -n sft python=3.10
conda activate sft
pip install -r requirements.txt
bash aearpo_train_sft/sft_train.sh
```
