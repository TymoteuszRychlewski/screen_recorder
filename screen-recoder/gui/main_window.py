import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox, QMessageBox,
    QLineEdit, QLabel, QFileDialog, QSpinBox, QHBoxLayout, QCheckBox
)
from PyQt5.QtCore import QSettings, QTimer
from recorder.screen_recorder import start_recording, stop_recording
from recorder.screen_utils import get_available_screens, get_window_list, get_mouse_selected_area
from datetime import datetime



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(100, 100, 400, 450)

        self.capture_mode_selector = QComboBox()
        self.capture_mode_selector.addItems(["screen", "section", "area"])
        self.capture_mode_selector.currentIndexChanged.connect(self.update_mode_visibility)

        

        self.format_selector = QComboBox()
        self.format_selector.addItems(["mp4", "webm"])

        self.audio_input_checkbox = QCheckBox("Record Microphone (Input)")
        self.audio_output_checkbox = QCheckBox("Record System Audio (Output)")

        self.screen_selector = QComboBox()
        self.window_selector = QComboBox()
        self.update_screens()
        self.update_windows()

        self.filename_input = QLineEdit("output")
        self.browse_button = QPushButton("Select Save Location")
        self.output_path = QLineEdit("recordings/")

        self.delay_input = QSpinBox()
        self.delay_input.setRange(0, 60)
        self.delay_input.setValue(3)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 3600)
        self.duration_input.setValue(0)

        self.window_input = QLineEdit(":0.0")
        self.area_input = QLineEdit("0,0 1920x1080")
        self.select_area_button = QPushButton("Select Area with Mouse")
        self.select_area_button.clicked.connect(self.set_mouse_area)

        self.start_btn = QPushButton("Start Recording")
        self.stop_btn = QPushButton("Stop Recording")

        self.start_btn.clicked.connect(self.handle_start)
        self.stop_btn.clicked.connect(self.handle_stop)
        self.browse_button.clicked.connect(self.select_output_dir)

        self.fps_input = QSpinBox()
        self.fps_input.setRange(1, 250)
        self.fps_input.setValue(25)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Capture Mode:"))
        layout.addWidget(self.capture_mode_selector)

        layout.addWidget(QLabel("Video Format:"))
        layout.addWidget(self.format_selector)

        layout.addWidget(QLabel("Frames per second (FPS)"))
        layout.addWidget(self.fps_input)

        layout.addWidget(self.audio_input_checkbox)
        layout.addWidget(self.audio_output_checkbox)

        self.screen_label = QLabel("Monitor:")
        layout.addWidget(self.screen_label)
        layout.addWidget(self.screen_selector)

        self.window_label = QLabel("Window Title:")
        layout.addWidget(self.window_label)
        layout.addWidget(self.window_selector)

        layout.addWidget(QLabel("Filename:"))
        layout.addWidget(self.filename_input)

        layout.addWidget(QLabel("Save Path:"))
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)

        layout.addWidget(QLabel("Delay Before Start (s):"))
        layout.addWidget(self.delay_input)

        layout.addWidget(QLabel("Duration (0 = unlimited):"))
        layout.addWidget(self.duration_input)

        self.area_label = QLabel("Capture Area (X,Y WxH):")
        layout.addWidget(self.area_label)
        layout.addWidget(self.area_input)
        layout.addWidget(self.select_area_button)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)
        self.update_mode_visibility()

        self.settings = QSettings("ScreenRecorder", "Settings")
        self.load_settings()

        self.end_timer = QTimer()
        self.end_timer.setSingleShot(True)
        self.end_timer.timeout.connect(self.show_auto_stop_notification)

        self.stop_btn.setVisible(False)

    def load_settings(self):

        self.output_path.setText(self.settings.value("path", "recordings/"))
        self.delay_input.setValue(int(self.settings.value("delay", 3)))
        self.duration_input.setValue(int(self.settings.value("duration", 0)))
        self.fps_input.setValue(int(self.settings.value("fps", 25)))
        self.audio_input_checkbox.setChecked(self.settings.value("record_input", "false") == "true")
        self.audio_output_checkbox.setChecked(self.settings.value("record_output", "false") == "true")

    def handle_stop(self):
        stop_recording(wait=True)
        self.end_timer.stop()
        QMessageBox.information(self, "Recording Finished", "Recording has been successfully stopped.")
        self.stop_btn.setVisible(False)


    def update_mode_visibility(self):
        mode = self.capture_mode_selector.currentText()

        self.screen_selector.setVisible(mode == "screen")
        self.screen_label.setVisible(mode == "screen")

        self.window_selector.setVisible(mode == "section")
        self.window_label.setVisible(mode == "section")

        self.area_input.setVisible(mode == "area")
        self.select_area_button.setVisible(mode == "area")
        self.area_label.setVisible(mode == "area")

    def update_screens(self):
        self.screen_selector.clear()
        screens = get_available_screens()
        self.screen_selector.addItems([screen["name"] for screen in screens])

    def update_windows(self):
        self.window_selector.clear()
        windows = get_window_list()
        self.window_selector.addItems(windows)

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if directory:
            self.output_path.setText(directory)

    def set_mouse_area(self):
        area = get_mouse_selected_area()
        if area:
            self.area_input.setText(area)

    def show_auto_stop_notification(self):
        QMessageBox.information(self, "Recording Finished", "Recording has finished automatically.")
        self.stop_btn.setVisible(False)


    def handle_start(self):
        selected_screen_index = self.screen_selector.currentIndex()
        all_screens = get_available_screens()

        if 0 <= selected_screen_index < len(all_screens):
            screen_info = all_screens[selected_screen_index]
        else:
            screen_info = {"pos": "0,0", "size": "1920x1080"}  

        filename = self.filename_input.text().strip()
        if not filename or filename.lower() == "output":
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"output_{timestamp}"
            self.filename_input.setText(filename)

        output_file = os.path.join(self.output_path.text(), f"{filename}.{self.format_selector.currentText()}")

        if os.path.exists(output_file):
            reply = QMessageBox.question(
                self,
                "File Exists",
                f"The file '{output_file}' already exists.\nDo you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        settings = {
            "format": self.format_selector.currentText(),
            "filename": filename,
            "path": self.output_path.text(),
            "delay": self.delay_input.value(),
            "duration": self.duration_input.value(),
            "fps": self.fps_input.value(),
            "display": self.window_input.text(),
            "mode": self.capture_mode_selector.currentText(),
            "screen": screen_info,
            "area": self.area_input.text(),
            "window": self.window_selector.currentText(),
            "record_input": self.audio_input_checkbox.isChecked(),
            "record_output": self.audio_output_checkbox.isChecked()
        }

        try:
            self.settings.setValue("filename", filename)
            self.settings.setValue("path", self.output_path.text())
            self.settings.setValue("delay", self.delay_input.value())
            self.settings.setValue("duration", self.duration_input.value())
            self.settings.setValue("fps", self.fps_input.value())
            self.settings.setValue("record_input", str(self.audio_input_checkbox.isChecked()).lower())
            self.settings.setValue("record_output", str(self.audio_output_checkbox.isChecked()).lower())
            start_recording(settings)

            if self.duration_input.value() > 0:
                self.end_timer.start(self.duration_input.value() * 1000)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        self.stop_btn.setVisible(True)

        




def launch_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
