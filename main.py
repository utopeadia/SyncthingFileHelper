import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow
from syncthing_connector import SyncthingConnector
from file_manager import FileManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    syncthing = SyncthingConnector(api_key='nTWZUVQtWzfp4SpuH9iuNxf7G4jzV6tU')
    file_manager = FileManager(syncthing)
    main_window = MainWindow(syncthing, file_manager)
    main_window.show()
    sys.exit(app.exec_())
