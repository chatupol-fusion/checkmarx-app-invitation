import helper
import checkmarx
import internal_log

def main():
    filepath_config = helper.read_args()
    configs = helper.read_config(filepath_config)
    init_checkmarx(configs)
    init_log(configs)
    invitations = read_invitations(configs)
    invite_status_rows = []
    for invitation in invitations:
        invite_status, app_name, grp_name, desc = checkmarx.invite_to_application(invitation)
        status_row = {
            'app_name' : app_name,
            'group_name' : grp_name,
            'invitation_status' : invite_status,
            'description' : desc
        }
        invite_status_rows.append(status_row)

    internal_log.generate_result_csv_with_timestamp(invite_status_rows)

def init_checkmarx(configs: dict):
    env_client_secret_name = configs["credentials"]["env_client_secret_name"]
    cli_sec = helper.read_env(env_client_secret_name)
    checkmarx.client_secret = cli_sec
    tenant = configs["checkmarx"]["tenant"]
    checkmarx.tenant = tenant
    checkmarx.login()

def init_log(configs: dict):
    log_dir = configs['common']['log_dir']
    internal_log.init_log_file(log_dir)

def read_invitations(configs: dict)->list[dict]:
    invitation_filepath = configs["common"]["invitations_csv_filepath"]
    invitations = helper.read_csv_invitations_data(invitation_filepath)
    return invitations

if __name__ == "__main__":
    main()