import csv
import datetime
import logging
import os
from pathlib import Path

__start_running_time = ''
__log_file_name = ''
__result_file_name = ''

def init_log_file(log_dir: str):
    __start_running_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    global __log_file_name
    __log_file_name = f'{log_dir}/log_{__start_running_time}.log'
    log_path = Path(__log_file_name)
    log_path.touch(exist_ok=True)
    setup_logger(log_path)

    global __result_file_name
    __result_file_name = f'{log_dir}/result_{__start_running_time}.csv'
    result_file_name_path = Path(__result_file_name)
    result_file_name_path.touch(exist_ok=True)

def setup_logger(log_file_path: str):
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a"
    )
    return


def append_to_csv(filename, new_data):
    # 1. Check if file exists (returns True/False)
    file_exists = os.path.isfile(filename)

    # 2. Open in 'a' (Append) mode
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        # Define your columns
        fieldnames = ["id", "app_name", "status"]
        
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 3. Smart Header Logic:
        # Only write the header if the file is NEW (did not exist before)
        if not file_exists:
            writer.writeheader()

        # 4. Append the new rows
        writer.writerows(new_data)
        print(f"Appended {len(new_data)} rows to {filename}")



def generate_result_csv_with_timestamp(data: dict):
    filename = __result_file_name
    # data = [
    #     {"id": 101, "app_name": "pet_store", "status": "active"},
    #     {"id": 102, "app_name": "shop_front", "status": "failed"},
    #     {"id": 103, "app_name": "payment_api", "status": "active"},
    # ]

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ["app_name", "group_name", "invitation_status", "description"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
        print("the result has been saved")
        
    except IOError as e:
        print(f"unable to write result: {e}")

def error_log(msg: str):
    logging.error(msg)
    return

def info_log(msg: str):
    logging.info(msg)
    return