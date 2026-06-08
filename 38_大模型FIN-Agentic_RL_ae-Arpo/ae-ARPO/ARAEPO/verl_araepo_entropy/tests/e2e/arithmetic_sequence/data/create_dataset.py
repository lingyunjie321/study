import os

from torch.utils import data

from tests.e2e.envs.digit_completion import DigitCompletion

if __name__ == "__main__":
    simple_task = DigitCompletion(max_number=9, max_diff=9, max_num_in_response=9)
    all_prompts = simple_task.get_all_prompts()

    # 21 * 6 * 4
    train_data, test_data = data.random_split(all_prompts, lengths=[0.8, 0.2])
    train_data = list(train_data)
    test_data = list(test_data)

    train_data = [[{"role": "user", "content": str(item)}] for item in train_data]
    test_data = [[{"role": "user", "content": str(item)}] for item in test_data]

    print(f"Size of train: {len(train_data)}, size of test: {len(test_data)}")

    train_data = {"prompt": train_data}
    test_data = {"prompt": test_data}

    model_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    import pandas as pd

    train_data_frame = pd.DataFrame(train_data)
    test_data_frame = pd.DataFrame(test_data)

    train_data_frame.to_parquet(os.path.join(model_folder, "train.parquet"))
    test_data_frame.to_parquet(os.path.join(model_folder, "test.parquet"))
