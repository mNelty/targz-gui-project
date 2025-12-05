
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QStackedWidget, QSplitter, QLabel,
                             QTextEdit, QListWidget, QTreeView, QMessageBox,
                             QPushButton)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from ..core.installer import Installer
from ..core.db_manager import DBManager
from .stylesheet import STYLESHEET

# --- Global DB Manager ---
config_dir = os.path.expanduser("~/.config/library")
os.makedirs(config_dir, exist_ok=True)
APP_DB_PATH = os.path.join(config_dir, "library.db")
db_manager = DBManager(APP_DB_PATH)


class Worker(QThread):
    """
    Worker thread to run the installation process without freezing the GUI.
    """
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    dependency_found = pyqtSignal(str) # New signal for dependency issues

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        installer = Installer(self.file_path, 
                              log_callback=self.progress.emit, 
                              db_manager=db_manager)
        
        extracted_path = installer.extract_package()
        if not extracted_path:
            self.finished.emit("Failed to extract package.")
            return
        
        success, result = installer.run_installation()
        
        if success:
            self.finished.emit("Installation completed successfully!")
        else:
            # Check if it's a dependency issue
            if isinstance(result, dict) and result.get("type") == "dependency":
                self.dependency_found.emit(result.get("package"))
            else:
                self.finished.emit(f"Installation failed: {result}")
            
        installer.cleanup()
        self.progress.emit("Cleanup complete.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LibRARx - .tar.gz Installer')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(STYLESHEET)

        self.setAcceptDrops(True)
        self.current_archive_path = None

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Splitter ---
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # --- Left Panel (with Stacked Widget) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.left_stack = QStackedWidget()
        left_layout.addWidget(self.left_stack)

        # --- Right Panel ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.details_viewer = QTextEdit()
        self.details_viewer.setReadOnly(True)
        right_layout.addWidget(self.details_viewer)

        # --- Bottom Log Area ---
        bottom_panel = QWidget()
        bottom_layout = QVBoxLayout(bottom_panel)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        bottom_layout.addWidget(self.log_viewer)

        # --- Assemble Panels ---
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(splitter)
        main_splitter.addWidget(bottom_panel)
        main_layout.addWidget(main_splitter)

        # --- Create Views for Left Stack ---
        self.create_history_view()
        self.create_contents_view()

        # --- Populate History View ---
        self.populate_history_list()

    def create_history_view(self):
        self.history_view = QWidget()
        layout = QVBoxLayout(self.history_view)
        layout.addWidget(QLabel("Installation History"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_selected)
        layout.addWidget(self.history_list)
        self.left_stack.addWidget(self.history_view)

    def create_contents_view(self):
        self.contents_view = QWidget()
        layout = QVBoxLayout(self.contents_view)
        layout.addWidget(QLabel("Archive Contents"))
        self.contents_tree = QTreeView()
        self.contents_model = QStandardItemModel()
        self.contents_tree.setModel(self.contents_model)
        self.contents_tree.setHeaderHidden(True)
        self.contents_tree.clicked.connect(self.on_contents_item_clicked)
        layout.addWidget(self.contents_tree)

        self.back_to_history_button = QPushButton("Back to History")
        self.back_to_history_button.clicked.connect(self.show_history_view)
        layout.addWidget(self.back_to_history_button)

        self.proceed_button = QPushButton("Proceed with Installation")
        self.proceed_button.clicked.connect(self.start_installation)
        layout.addWidget(self.proceed_button)

        self.left_stack.addWidget(self.contents_view)

    def populate_history_list(self):
        self.history_list.clear()
        packages = db_manager.get_all_packages()
        for pkg in packages:
            self.history_list.addItem(f"{pkg['name']} ({pkg['version']})")

    def on_history_item_selected(self, item):
        package_name = item.text().split(' ')[0]
        details = db_manager.get_package_details(package_name)
        if details:
            details_text = (
                f"Name: {details['name']}\n"
                f"Version: {details['version']}\n"
                f"Installed: {details['install_date']}\n\n"
                f"Files:\n" + "\n".join(details['files'])
            )
            self.details_viewer.setText(details_text)
        else:
            self.details_viewer.setText(f"Could not find details for {package_name}")

    def show_history_view(self):
        self.left_stack.setCurrentWidget(self.history_view)

    def show_contents_view(self, file_path):
        self.current_archive_path = file_path
        self.populate_contents_tree(file_path)
        self.left_stack.setCurrentWidget(self.contents_view)

    def populate_contents_tree(self, archive_path):
        self.contents_model.clear()
        members = Installer.list_archive_contents(archive_path)

        root_item = self.contents_model.invisibleRootItem()
        path_map = {'': root_item}

        for member in sorted(members, key=lambda x: x.name):
            path_parts = member.name.strip('/').split('/')
            parent_path = ''
            parent = root_item

            for part in path_parts[:-1]:
                parent_path += part + '/'
                if parent_path in path_map:
                    parent = path_map[parent_path]
                else:
                    new_parent = QStandardItem(part)
                    parent.appendRow(new_parent)
                    path_map[parent_path] = new_parent
                    parent = new_parent

            item = QStandardItem(path_parts[-1])
            item.setData(member.name, Qt.UserRole)
            item.setEditable(False)
            parent.appendRow(item)

    def on_contents_item_clicked(self, index):
        item = self.contents_model.itemFromIndex(index)
        member_name = item.data(Qt.UserRole)

        if member_name and self.current_archive_path:
            is_dir = member_name.endswith('/')
            if not is_dir:
                content = Installer.read_file_from_archive(self.current_archive_path, member_name)
                self.details_viewer.setText(content)
            else:
                self.details_viewer.setText(f"--- Directory: {member_name} ---")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toLocalFile().endswith('.tar.gz'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.show_contents_view(file_path)

    def start_installation(self):
        if self.current_archive_path:
            self.log_viewer.clear()
            self.worker = Worker(self.current_archive_path)
            self.worker.progress.connect(self.update_log)
            self.worker.finished.connect(self.on_installation_finished)
            self.worker.dependency_found.connect(self.handle_dependency_issue)
            self.worker.start()
        else:
            self.update_log("No archive selected for installation.")

    def update_log(self, message):
        self.log_viewer.append(message)

    def on_installation_finished(self, message):
        self.log_viewer.append(f"\n--- FINISHED ---\n{message}")

    def handle_dependency_issue(self, package_name):
        self.update_log(f"Dependency issue: A required package '{package_name}' seems to be missing.")
        # QMessageBox will be restyled later
        reply = QMessageBox.question(self, 'Missing Dependency',
                                     f"The package '{package_name}' appears to be missing.\n\n"
                                     f"Would you like to try installing it?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.update_log(f"User approved installation of '{package_name}'.")
        else:
            self.update_log("User declined to install the dependency. Installation aborted.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
