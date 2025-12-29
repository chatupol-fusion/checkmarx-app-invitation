import helper
import checkmarx

def main():
    filepath_config = helper.read_args()
    configs = helper.read_config(filepath_config)
    init_checkmarx(configs)
    invitations = read_invitations(configs)
    for invitation in invitations:
        checkmarx.invite_to_application(invitation)

def init_checkmarx(configs: dict):
    env_client_secret_name = configs["credentials"]["env_client_secret_name"]
    cli_sec = helper.read_env(env_client_secret_name)
    checkmarx.client_secret = cli_sec
    tenant = configs["checkmarx"]["tenant"]
    checkmarx.tenant = tenant
    checkmarx.login()

def read_invitations(configs: dict)->list[dict]:
    invitation_filepath = configs["common"]["invitations_csv_filepath"]
    invitations = helper.read_csv_invitations_data(invitation_filepath)
    return invitations

if __name__ == "__main__":
    main()