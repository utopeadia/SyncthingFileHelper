from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QAction, QMenu
from PyQt5.QtCore import Qt
from syncthing_connector import SyncthingConnector
from file_manager import FileManager
import os

class MainWindow(QMainWindow):
    def __init__(self, syncthing, file_manager):
        super().__init__()

        self.setWindowTitle("Syncthing On-Demand Sync")
        self.setGeometry(100, 100, 800, 600)

        self.syncthing = syncthing
        self.file_manager = file_manager

        self.file_tree = QTreeWidget(self)
        self.file_tree.setHeaderLabel("Shared Folders")
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.on_context_menu)

        self.setCentralWidget(self.file_tree)

        self.load_file_tree()

    def load_file_tree(self):
        self.file_manager.load_file_tree(self.file_tree)

    def on_context_menu(self, pos):
        item = self.file_tree.itemAt(pos)
        if item is None or item.parent() is None:
            return

        menu = QMenu(self)
        free_up_space_action = QAction("Free Up Space", self)
        free_up_space_action.triggered.connect(lambda: self.free_up_space(item))
        menu.addAction(free_up_space_action)

        always_keep_on_device_action = QAction("Always Keep on Device", self)
        always_keep_on_device_action.triggered.connect(lambda: self.always_keep_on_device(item))
        menu.addAction(always_keep_on_device_action)

        menu.exec_(self.file_tree.viewport().mapToGlobal(pos))

    def free_up_space(self, item):
        folder_id = self.get_folder_id(item.parent())
        file_path = self.get_file_path(item, folder_id)
        self.file_manager.free_up_space(folder_id, file_path)
        self.load_file_tree()

    def always_keep_on_device(self, item):
        folder_id = self.get_folder_id(item.parent())
        file_path = self.get_file_path(item, folder_id)
        self.file_manager.always_keep_on_device(folder_id, file_path)
        self.load_file_tree()

    def get_folder_id(self, folder_item):
        for folder in self.syncthing.get_shared_folders():
            if folder['name'] == folder_item.text(0):
                return folder['id']
        return None

    def get_file_path(self, file_item, folder_id):
        folder_path = self.syncthing.get_folder_path(folder_id)
        return os.path.join(folder_path, file_item.text(0))

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow("YOUR_SYNCTHING_API_KEY")
    window.show()
    app.exec_()
