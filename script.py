import yaml
import subprocess


def modify_config_and_run_backtest():
    config_file = 'config.yaml'

    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    for time_length in range(14, 361):
        config['data']['time_length_days'] = time_length

        with open(config_file, 'w') as file:
            yaml.dump(config, file)

        print(f"Running backtest with time_length_days = {time_length}...")

        subprocess.run(['python3', 'main.py'])


if __name__ == "__main__":
    modify_config_and_run_backtest()
