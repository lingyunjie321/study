"""Utilities for distributed training."""

import os

import torch.distributed

from verl.utils.device import get_torch_device, is_cuda_available


def initialize_global_process_group(timeout_second=36000):
    from datetime import timedelta

    torch.distributed.init_process_group("nccl" if is_cuda_available else "hccl", timeout=timedelta(seconds=timeout_second))
    local_rank = int(os.environ["LOCAL_RANK"])
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])

    if torch.distributed.is_initialized():
        get_torch_device().set_device(local_rank)
    return local_rank, rank, world_size


def destroy_global_process_group():
    if torch.distributed.is_initialized():
        torch.distributed.destroy_process_group()
