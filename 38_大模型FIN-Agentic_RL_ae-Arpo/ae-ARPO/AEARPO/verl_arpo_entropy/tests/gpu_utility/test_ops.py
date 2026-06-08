def test_flash_attn_cross_entropy():
    import torch
    from flash_attn.ops.triton.cross_entropy import cross_entropy_loss
    from torch import nn

    from verl.utils.debug import log_gpu_memory_usage
    from verl.utils.torch_functional import logprobs_from_logits_naive

    log_gpu_memory_usage("At start")

    hidden_states = torch.randn(size=(2048, 5120), device="cuda", requires_grad=True, dtype=torch.bfloat16)

    linear = nn.Linear(in_features=5120, out_features=155136, bias=False, device="cuda", dtype=torch.bfloat16)

    logits = linear(hidden_states)

    # logits = logits.float()
    labels = torch.randint(low=0, high=155136, size=(2048,), device="cuda")

    log_gpu_memory_usage("before computation")
    # output = checkpoint.checkpoint(logprobs_from_logits, logits, labels, use_reentrant=True)
    output = -cross_entropy_loss(logits, labels)[0]
    # output = logprobs_from_logits(logits, labels)
    log_gpu_memory_usage("After forward")
    output.sum().backward()
    log_gpu_memory_usage("After backward")

    groundtruth = logprobs_from_logits_naive(logits.float(), labels)

    torch.testing.assert_close(output, groundtruth)
