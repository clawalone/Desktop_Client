import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.settings import Settings
from src.logging_config import configure_logging


def main():
    configure_logging()
    settings = Settings.load()

    app = QApplication(sys.argv)
    window = MainWindow(settings)
    window.setWindowTitle(settings.app_name)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
