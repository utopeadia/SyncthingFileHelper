from PyQt5.QtWidgets import QTreeWidgetItem
import os
import requests

class FileManager:
    def __init__(self, syncthing):
        self.syncthing = syncthing

    def load_file_tree(self, file_tree):
        """Loads the file tree from Syncthing."""
        file_tree.clear()
        root_item = QTreeWidgetItem(file_tree, ["Shared Folders"])

        # Get shared folders from Syncthing
        shared_folders = self.syncthing.get_shared_folders()
        if shared_folders:
            for folder in shared_folders:
                folder_item = QTreeWidgetItem(root_item, [folder['name']])

                # Get files in the folder
                files = self.syncthing.get_files_in_folder(folder['id'])
                if files:
                    for file in files:
                        QTreeWidgetItem(folder_item, [file['name']])
        else:
            QTreeWidgetItem(root_item, ["Error loading shared folders"])

    def free_up_space(self, folder_id, file_path):
        """Removes the local copy of a file, marking it for on-demand download."""
        # Get the current .stignore patterns
        stignore_path = self.get_stignore_path(folder_id)
        if not stignore_path:
            print(f"Could not find .stignore for folder {folder_id}")
            return

        try:
            with open(stignore_path, "r") as f:
                stignore_patterns = f.readlines()
        except FileNotFoundError:
            stignore_patterns = []

        # Add the file to .stignore to exclude it from syncing
        relative_file_path = os.path.relpath(file_path, self.syncthing.get_folder_path(folder_id))
        ignore_pattern = f"//{relative_file_path}\n"
        if ignore_pattern not in stignore_patterns:
            stignore_patterns.append(ignore_pattern)

            with open(stignore_path, "w") as f:
                f.writelines(stignore_patterns)

        # Delete the local file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed local file: {file_path}")
        else:
            print(f"File does not exist locally: {file_path}")
        
        # Rescan the folder
        self.syncthing.rescan_folder(folder_id)

    def always_keep_on_device(self, folder_id, file_path):
        """Ensures a file is always kept on the device."""
        # Get the current .stignore patterns
        stignore_path = self.get_stignore_path(folder_id)
        if not stignore_path:
            print(f"Could not find .stignore for folder {folder_id}")
            return

        try:
            with open(stignore_path, "r") as f:
                stignore_patterns = f.readlines()
        except FileNotFoundError:
            stignore_patterns = []

        # Remove the file from .stignore if it's there
        relative_file_path = os.path.relpath(file_path, self.syncthing.get_folder_path(folder_id))
        ignore_pattern = f"//{relative_file_path}\n"
        if ignore_pattern in stignore_patterns:
            stignore_patterns.remove(ignore_pattern)

            with open(stignore_path, "w") as f:
                f.writelines(stignore_patterns)

        # Trigger a download if the file doesn't exist locally
        if not os.path.exists(file_path):
            # There isn't a direct way to force Syncthing to download a specific file
            # Rescanning will eventually sync the file
            self.syncthing.rescan_folder(folder_id)
            print(f"File marked for download: {file_path}")
        else:
            print(f"File already exists locally: {file_path}")
        
        # Rescan the folder
        self.syncthing.rescan_folder(folder_id)

    def get_stignore_path(self, folder_id):
        """Gets the path to the .stignore file for a given folder."""
        config = self.syncthing.get_config()
        for folder in config.get('folders', []):
            if folder['id'] == folder_id:
                return os.path.join(folder['path'], '.stignore')
        return None
