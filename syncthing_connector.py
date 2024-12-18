import requests

class SyncthingConnector:
    def __init__(self, api_key, url="http://localhost:8384"):
        self.url = url
        self.headers = {
            "X-API-Key": api_key,
        }

    def connect(self):
        """Tests the connection to Syncthing."""
        try:
            response = requests.get(f"{self.url}/rest/system/ping", headers=self.headers)
            if response.status_code == 200:
                return True
            else:
                print(f"Connection failed with status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("Failed to connect to Syncthing. Make sure it's running and the URL is correct.")
            return False

    def get_shared_folders(self):
        """Gets the list of shared folders from Syncthing."""
        try:
            response = requests.get(f"{self.url}/rest/system/config", headers=self.headers)
            response.raise_for_status()
            config = response.json()
            folders = config.get('folders', [])
            return [{'id': folder['id'], 'name': folder['label']} for folder in folders]
        except requests.exceptions.RequestException as e:
            print(f"Error getting shared folders: {e}")
            return []

    def get_files_in_folder(self, folder_id):
        """Gets the list of files in a specific folder from Syncthing."""
        try:
            response = requests.get(f"{self.url}/rest/db/browse", headers=self.headers, params={"folder": folder_id, "levels": 1})
            response.raise_for_status()
            files = response.json()
            return [{'name': file['name']} for file in files if file['type'] == 'file']
        except requests.exceptions.RequestException as e:
            print(f"Error getting files in folder {folder_id}: {e}")
            return []

    def get_folder_path(self, folder_id):
        """Gets the path of a specific folder from Syncthing."""
        try:
            response = requests.get(f"{self.url}/rest/system/config", headers=self.headers)
            response.raise_for_status()
            config = response.json()
            for folder in config.get('folders', []):
                if folder['id'] == folder_id:
                    return folder['path']
            return None  # Folder ID not found
        except requests.exceptions.RequestException as e:
            print(f"Error getting folder path for {folder_id}: {e}")
            return None
