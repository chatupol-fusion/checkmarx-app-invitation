from enum import Enum
import requests
import internal_log

token = ""
client_secret = ""
tenant = ""

class InviteStatus(str, Enum):
    DONE = "done"
    SKIP = "skip"
    FAILED = "failed"

def invite_to_application(invitation: dict) -> tuple[InviteStatus, str, str, str]:
    app_name = invitation["app_name"]
    app = fetch_application_by_name(app_name)
    if not app:
        log_msg = f'unable to fetch application by name: {app_name}'
        internal_log.error_log(log_msg)
        return InviteStatus.FAILED, app_name, "unknown", log_msg
    
    grp_name = "AppGroup_" + app_name
    done_grp_creating = create_group(grp_name, tenant)
    if not done_grp_creating:
        log_msg = f'unable to create group, name: {grp_name}'
        internal_log.error_log(log_msg)
        return InviteStatus.FAILED, app_name, grp_name, log_msg

    grp = fetch_group_by_name(grp_name=grp_name)
    if not grp:
        log_msg = f'unable to fetch group by name: {grp_name}'
        internal_log.error_log(log_msg)
        return InviteStatus.FAILED, app_name, grp_name, log_msg

    grp_id = grp['id']
    app_id = app['applications'][0]['id']
    is_assigned = check_is_assign_group(grp_id, app_id)
    if is_assigned:
        log_msg = f'the group name: {grp_name} has been assigned to the application: {app_name}'
        internal_log.info_log(log_msg)
        return InviteStatus.SKIP, app_name, grp_name, log_msg

    is_assigned = assign_group_to_application(grp_id=grp_id,application_id=app_id)
    if not is_assigned:
        log_msg = f'unable to assign group name: {grp_name} to the application: {app_name}'
        internal_log.error_log(log_msg)
        return InviteStatus.FAILED, app_name, grp_name, log_msg

    # emails = invitation["email_list"]
    # invite_email_to_group(grp_id, emails)
    return InviteStatus.DONE, app_name, grp_name, ""

def invite_email_to_group(grp_id: str, email_list: list):
    for email in email_list:
        assign_user_to_group(email, grp_id)

def login():
    url = f'https://sng.iam.checkmarx.net/auth/realms/{tenant}/protocol/openid-connect/token'
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded',
    }
    payload = {
        'grant_type' : 'client_credentials',
        'client_id' : 'api-client',
        'client_secret' : client_secret
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            resp = response.json()
            global token 
            token = resp["access_token"]
        else:
            internal_log.error_log(f"unable to login: {response.text}")
            
    except Exception as e:
        internal_log.error_log(f"Error: {e}")

def fetch_application_by_name(app_name: int) -> dict:
    url = f'https://sng.ast.checkmarx.net/api/applications?name={app_name}'
    data = call_api_get(url)
    if not isinstance(data, dict):
        internal_log.error_log(f"failed to get app for app_name: {app_name}")
        return

    return data

def fetch_application_by_id(app_id: int) -> dict:
    url = f'https://sng.ast.checkmarx.net/api/applications/{app_id}'
    data = call_api_get(url)
    if not isinstance(data, dict):
        internal_log.error_log(f"failed to get app for app_id: {app_id}")
        return

    return data

def create_group(grp_name: str, checkmarx_tenant: str) -> bool:
    url = f'https://sng.iam.checkmarx.net/auth/admin/realms/{checkmarx_tenant}/groups'
    payload = {
        "name": grp_name
    }
    try:
        resp = call_api_post(url, payload=payload)
    except Exception as e:
        return False

    return True

def fetch_group_by_name(grp_name: str) -> dict:
    url = f'https://sng.ast.checkmarx.net/api/access-management/groups?search={grp_name}&limit=1'
    data = call_api_get(url)
    if not isinstance(data, list):
        internal_log.error_log(f"failed to get group for group_name: {grp_name}")
        return
    
    if len(data) == 0:
        return {}

    return data[0]

def check_access(resource_type: str, resource_id: str):
    url = f'https://sng.ast.checkmarx.net/api/access-management/has-access?action=update-access&resource-id={resource_id}&resource-type={resource_type}'
    resp = call_api_get(url=url)
    internal_log.info_log(f'checkAccess resp {resp}')

def check_is_assign_group(grp_id: str, app_id: str)->bool:
    url = f'https://sng.ast.checkmarx.net/api/access-management?entity-id={grp_id}&resource-id={app_id}'

    resp = call_api_get(url=url)
    if isinstance(resp, dict):
        hasResourceFields = 'resourceID' in resp and 'resourceType' in resp and not resp['resourceID'] == "" and resp['resourceType'] == 'application'
        if hasResourceFields:
            return True

    return False

def assign_group_to_application(grp_id: str, application_id: str) -> bool:
    url = 'https://sng.ast.checkmarx.net/api/access-management/'
    payload = {
        "entityID": grp_id,
        "entityType": "group",
        "resourceID": application_id,
        "resourceType": "application"
    }

    resp = call_api_post(url=url, payload=payload)
    if not resp is None:
        return True
    
    return False

def assign_user_to_group(email: str, grp_id: str):
    return 

# ------------------------helper------------------------ #
# |                                                     |
# |                                                     |
# |                                                     |
# |                                                     |
# |                                                     |
# |                                                     |
# |                                                     |
# ------------------------helper------------------------ #

def call_api_get(url: str) -> dict:
    try:
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            internal_log.error_log(f"unable to call GET for: url {url} \t\terror_code: {response.status_code}\t\terror_msg: {response.text}")
    except Exception as e:
        internal_log.error_log(f"unable to call GET with unhandle error: {e}")

def call_api_post(url, payload) -> dict:
    try:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                return {}
        else:
            internal_log.error_log(f"unable to call POST for: url {url} \t\terror_code: {response.status_code}\t\terror_msg: {response.text}")
    except Exception as e:
        internal_log.error_log(f"unable to call POST with unhandle error: {e}")

