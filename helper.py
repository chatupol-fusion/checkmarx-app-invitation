import argparse
import csv
import os
import yaml

def read_args() -> tuple[str, dict]:
    parser = argparse.ArgumentParser(description="My Python Script CLI")
    parser.add_argument("--config", type=str,default="configs.yaml", required=False, help="The path to the configs file")
    parser.add_argument("--invitation-file", type=str,default="data/invitation.csv", required=False, help="The path to the invitation file, overide configuation")
    parser.add_argument("--action", type=str, default="grp-to-app", required=False, help="The action includes [grp-to-app, invoke-grp-from-app, email-to-grp, email-to-app]")
    args = parser.parse_args()
    overide_configs = {
        'invitation_file_path': args.invitation_file,
        'action': args.action
    }
    return args.config, overide_configs

def read_config(filename: str):
    """
    Reads a YAML file and returns a dictionary.
    """
    try:
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None

def read_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    return env_value

def read_csv_invitations_data(filename: str) -> list[dict]:
    results = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            app_name = row['app_name'].strip()
            raw_emails = row['email_list']
            email_list = raw_emails.split('|')
            
            results.append({
                "app_name": app_name,
                "email_list": email_list
            })
            
    return results