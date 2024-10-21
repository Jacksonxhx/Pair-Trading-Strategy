import time
import yaml
import subprocess
import os


def run_backtests():
    config_file = 'config.yaml'

    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # 定义参数范围
    window_values = [i for i in range(5, 51, 5)] + [i for i in range(60, 150, 10)] + [390, 1950]
    z_threshold_values = [1, 1.5, 2, 2.5, 3]
    time_length_days_values = [15] + [i for i in range(30, 361, 10)]
    training_threshold_values = [1.5, 2, 3, 5, 10]

    # 创建保存结果的目录
    results_dir = 'backtest_results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # 控制变量法：一次只改变一个参数，其他参数保持默认值
    default_params = {
        'window': config['strategy']['window'],
        'z_threshold': config['strategy']['z_threshold'],
        'time_length_days': config['data']['time_length_days'],
        'training_threshold': config['data']['training_threshold'],
    }

    # 测试 window 参数
    for window in window_values:
        config['strategy']['window'] = window
        config['strategy']['z_threshold'] = default_params['z_threshold']
        config['data']['time_length_days'] = default_params['time_length_days']
        config['data']['training_threshold'] = default_params['training_threshold']

        with open(config_file, 'w') as file:
            yaml.dump(config, file)

        print(f"Running backtest with window = {window}...")
        result_name = f"result_window_{window}.csv"
        subprocess.run(['python3', 'main.py', os.path.join(results_dir, result_name), "backtest_results/json/window.json"])

        time.sleep(3)

    # 测试 z_threshold 参数
    for z_threshold in z_threshold_values:
        config['strategy']['window'] = default_params['window']
        config['strategy']['z_threshold'] = z_threshold
        config['data']['time_length_days'] = default_params['time_length_days']
        config['data']['training_threshold'] = default_params['training_threshold']

        with open(config_file, 'w') as file:
            yaml.dump(config, file)

        print(f"Running backtest with z_threshold = {z_threshold}...")
        result_name = f"result_z_threshold_{z_threshold}.csv"
        subprocess.run(['python3', 'main.py', os.path.join(results_dir, result_name), "backtest_results/json/z_threshold.json"])

        time.sleep(1)

    # 测试 time_length_days 参数
    for time_length in time_length_days_values:
        config['strategy']['window'] = default_params['window']
        config['strategy']['z_threshold'] = default_params['z_threshold']
        config['data']['time_length_days'] = time_length
        config['data']['training_threshold'] = default_params['training_threshold']

        with open(config_file, 'w') as file:
            yaml.dump(config, file)

        print(f"Running backtest with time_length_days = {time_length}...")
        result_name = f"result_time_length_{time_length}d.csv"
        subprocess.run(['python3', 'main.py', os.path.join(results_dir, result_name), "backtest_results/json/time_length.json"])

        time.sleep(1)

    # 测试 training_threshold 参数
    for training_threshold in training_threshold_values:
        config['strategy']['window'] = default_params['window']
        config['strategy']['z_threshold'] = default_params['z_threshold']
        config['data']['time_length_days'] = default_params['time_length_days']
        config['data']['training_threshold'] = training_threshold

        with open(config_file, 'w') as file:
            yaml.dump(config, file)

        print(f"Running backtest with training_threshold = {training_threshold}...")
        result_name = f"result_training_threshold_{training_threshold}.csv"
        subprocess.run(['python3', 'main.py', os.path.join(results_dir, result_name), "backtest_results/json/threshold.json"])

        time.sleep(1)

    # print(f"Running backtest with all possibilities...")
    # for window in window_values:
    #     for z_threshold in z_threshold_values:
    #         for time_length in time_length_days_values:
    #             for training_threshold in training_threshold_values:
    #                 config['strategy']['window'] = window
    #                 config['strategy']['z_threshold'] = z_threshold
    #                 config['data']['time_length_days'] = time_length
    #                 config['data']['training_threshold'] = training_threshold
    #
    #                 with open(config_file, 'w') as file:
    #                     yaml.dump(config, file)
    #
    #                 result_name = f"result_all_combinations.csv"
    #                 subprocess.run(['python3', 'main.py', os.path.join(results_dir, result_name),
    #                                 "backtest_results/json/all.json"])
    #
    #                 time.sleep(1)


    # 最后，测试最佳参数组合
    # 假设您通过上述测试得到了最佳参数值
    # best_params = {
    #     'window': 125,
    #     'z_threshold': 1.5,
    #     'time_length_days': 180,
    #     'training_threshold': 3,
    # }
    #
    # config['strategy']['window'] = best_params['window']
    # config['strategy']['z_threshold'] = best_params['z_threshold']
    # config['data']['time_length_days'] = best_params['time_length_days']
    # config['data']['training_threshold'] = best_params['training_threshold']
    #
    # with open(config_file, 'w') as file:
    #     yaml.dump(config, file)
    #
    # print(f"Running backtest with best parameter combination...")
    # result_name = f"result_best_params.csv"
    # subprocess.run(['python3', 'main.py', os.path.join(results_dir, result_name)])

    print("Backtesting completed.")


if __name__ == "__main__":
    run_backtests()

