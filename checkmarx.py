import json
import requests

token = ""
client_secret = ""
tenant = ""
__headers = {
    'Accept': 'application/json; version=1.0',
    'Authorization': f'Bearer {token}'
}

def invite_to_application(invitation: dict):
    app_name = invitation["app_name"]
    app = fetch_application_by_name(app_name)
    if not app:
        return
    
    
    grp_name = "AppName_" + app_name
    grp_id = create_group(grp_name, tenant)
    app_id = app['applications'][0]['id']
    assign_group_to_application(grp_id, app_id)
    emails = invitation["email_list"]
    for email in emails:
        assign_user_to_group(email, grp_id)

    return

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
            print(f"unable to login: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def fetch_application_by_name(app_name: int) -> dict:
    url = f'https://sng.ast.checkmarx.net/api/applications?name={app_name}'
    data = call_api_get(url)
    if not isinstance(data, dict):
        print(f"failed to get app for app_name: {app_name}")
        return

    return data

def fetch_application_by_id(app_id: int) -> dict:
    url = f'https://sng.ast.checkmarx.net/api/applications/{app_id}'
    print(f'url: {url}')
    data = call_api_get(url)
    if not isinstance(data, dict):
        print(f"failed to get app for app_id: {app_id}")
        return

    return data

def create_group(grp_name: str, checkmarx_tenant: str) -> str:
    url = f'https://sng.iam.checkmarx.net/auth/admin/realms/{checkmarx_tenant}/groups'
    payload = {
        "name": grp_name
    }

    resp = call_api_post(url, payload=payload)
    print(f'resp: {resp}')
    return ""

def fetch_group_by_id(grp_id: str) -> dict:
    url = f'https://sng.ast.checkmarx.net/api/access-management/groups?ids={grp_id}'
    data = call_api_get(url)
    if not isinstance(data, list):
        print(f"failed to get group for group_id: {grp_id}")
        return

    return data

def assign_group_to_application(grp_id: str, application_id: str):
    return

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
        # print(f'headers: {headers}')
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed with status: {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error occurred: {e}")

def call_api_post(url, payload) -> dict:
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed: {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

