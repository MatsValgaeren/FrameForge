"""FrameForge provides a range of quick video editing functions.

- 10 MB / Discord Size: Compress a video to ensure it is under 10 MB, making it suitable for Discord uploads.
- Trim / Cut Video: Choose the start and end frames to extract a specific section of your video.
- Change Speed: Adjust the playback speed of your video.
- Combine Videos: Merge two videos into one.
- Image to Video: Create a video collage from a selected image directory.
- Extract Audio: Extract the audio track from a video file.
"""

__author__ = "Mats Valgaeren"
__contact__ = "contact@matsvalgaeren.com"
__date__ = "2025-05-07"
__license__ = "GPLv3"
__version__ = "0.1.1"


# Standard Library Imports
import glob
import math
import os
import pathlib
import shutil
import subprocess
import sys

# UI-Specific Imports (Third-Party)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
)


# Supported audio file extensions for validation and filtering
AUDIO_EXTENSIONS = [
    ".mp3", ".aac", ".m4a", ".m4b", ".m4p", ".wav", ".flac", ".alac", ".ogg", ".oga",
    ".opus", ".wma", ".aiff", ".aif", ".ape", ".wv", ".amr", ".awb", ".au", ".ra",
    ".rm", ".mp2", ".mp1", ".ac3", ".dts", ".caf", ".voc", ".tta", ".mka", ".spx",
    ".8svx", ".gsm", ".ivs", ".sln", ".vox", ".rf64", ".msv", ".dvf", ".act", ".dss"
]

# Supported image file extensions for validation and filtering
IMAGE_EXTENSIONS = [
    ".jpg", ".jpeg", ".jpe", ".jfif", ".pjpeg", ".pjp",
    ".png", ".gif", ".bmp", ".webp", ".avif", ".apng", ".tif", ".tiff",
    ".heif", ".heic", ".ico", ".cur", ".xbm", ".svg", ".svgz"
]

# Supported video file extensions for validation and filtering
VIDEO_EXTENSIONS = [
    ".mp4", ".m4v", ".m4p", ".mov", ".qt", ".avi", ".wmv", ".asf", ".flv", ".f4v",
    ".f4p", ".f4a", ".f4b", ".webm", ".mkv", ".mpg", ".mpeg", ".mp2", ".mpe", ".mpv",
    ".vob", ".dvd", ".3gp", ".3g2", ".svi", ".mxf", ".ogv", ".ogg", ".amv", ".rm",
    ".roq", ".nsv", ".yuv", ".gifv", ".mng", ".rrc", ".mod", ".dv"
]

# Supported audio file extensions and codecs for validation and extraction
AUDIO_CODEC_MAP = {
    ".mp3": "libmp3lame",
    ".flac": "flac",
    ".wav": "pcm_s16le",
    ".aac": "aac",
    ".m4a": "aac",
    ".alac": "alac",
    ".ogg": "libvorbis",
    ".opus": "libopus",
    ".wma": "wmav2",
    ".amr": "libopencore_amrnb",
    ".aiff": "pcm_s16be",
    ".au": "pcm_mulaw",
    ".ac3": "ac3",
    ".dts": "dca",
    ".wv": "wavpack",
    ".tta": "tta",
    ".mp2": "mp2",
    ".caf": "pcm_s16le",
}


class MessageUtils:
    """Utility class for displaying user messages and warnings via QMessageBox.

    Centralizes all user-facing messages for consistency and easier maintenance.
    """
    @staticmethod
    def invalid_video(parent):
        QMessageBox.warning(parent, "Invalid Input", "Please select a valid video file.")

    @staticmethod
    def invalid_audio(parent):
        QMessageBox.warning(parent, "Invalid Input", "Please select a valid audio file.")

    @staticmethod
    def no_audio_stream(parent):
        QMessageBox.critical(parent, "Audio Error", "The selected video has no audio stream.")

    @staticmethod
    def file_exists(parent):
        QMessageBox.warning(parent, "File Exists", "Please select a new file name that does not already exist.")

    @staticmethod
    def operation_failed(parent, details=""):
        QMessageBox.critical(parent, "Operation Failed", f"Something went wrong.\n{details}")

    @staticmethod
    def operation_success(parent, message="Operation completed successfully."):
        QMessageBox.information(parent, "Success", message)


class FFmpegGUI(QWidget):
    """
    Main application window for FrameForge:
    - handles navigation between different video/audio utility pages
    - manages shared state (file paths, video properties)
    - provides utility methods for file selection and validation
    """
    def __init__(self):
        super().__init__()
        self.check_ffmpeg_installed()
        self._init_variables()
        self._init_ui()

    def check_ffmpeg_installed(self):
        """ Checks if ffmpeg and ffprobe are installed and available in PATH."""
        for tool in ("ffmpeg", "ffprobe"):
            if shutil.which(tool) is None:
                QMessageBox.critical(self, "Missing Dependency", f"{tool} is not installed or not in PATH.")
                sys.exit(1)

    def _init_variables(self):
        self.images_dir = ''
        self.input_video = ''
        self.input_video_2 = ''
        self.output_video = ''
        self.output_audio = ''
        self.frame_rate, self.video_duration = 0, 0

    def _init_ui(self):
        self.side_ui_size = 80  # Standard width for side UI elements

        self.setWindowTitle("FrameForge")
        self.set_window_logo()
        self.layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()

        self.combo_box = QComboBox()
        self.combo_box.addItem("10 MB/ Discord Size")
        self.combo_box.addItem("Trim/ Cut Video")
        self.combo_box.addItem("Change Speed")
        self.combo_box.addItem("Combine 2 Videos")
        self.combo_box.addItem("Image to Video")
        self.combo_box.addItem("Extract Audio")

        self.compress_10mb_page = Compress10MBPage(self)
        self.trim_page = TrimPage(self)
        self.speed_page = SpeedPage(self)
        self.cat_page = CatPage(self)
        self.image_to_video_page = ImageToVideoPage(self)
        self.extract_sound_page = ExtractSoundPage(self)

        self.stacked_widget.addWidget(self.compress_10mb_page)
        self.stacked_widget.addWidget(self.trim_page)
        self.stacked_widget.addWidget(self.speed_page)
        self.stacked_widget.addWidget(self.cat_page)
        self.stacked_widget.addWidget(self.image_to_video_page)
        self.stacked_widget.addWidget(self.extract_sound_page)

        # Connect navigation to page switching and field synchronization
        self.combo_box.currentIndexChanged.connect(self.stacked_widget.setCurrentIndex)
        self.combo_box.currentIndexChanged.connect(self.update_directory_fields)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.stacked_widget)
        self.layout.setStretch(1, 0)
        self.setLayout(self.layout)

    def set_window_logo(self):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, ("FrameForgeLogo.ico"))
        print(icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("Can't find logo file.")

    def update_directory_fields(self):
        """
        Synchronize the file path fields in the current page with the main window's state.
        Called whenever the user switches between tool pages.
        """
        current_widget = self.stacked_widget.currentWidget()
        images_field = current_widget.findChild(QLineEdit, "images_dir_field")
        video_field = current_widget.findChild(QLineEdit, "input_video_field")
        video_field_2 = current_widget.findChild(QLineEdit, "input_video_field_2")
        output_video_field = current_widget.findChild(QLineEdit, "output_video_field")
        output_audio_field = current_widget.findChild(QLineEdit, "output_audio_field")

        if images_field:
            images_field.setText(self.images_dir)
        if video_field:
            video_field.setText(self.input_video)
        if video_field_2:
            video_field_2.setText(self.input_video_2)
        if output_video_field:
            output_video_field.setText(self.output_video)
        if output_audio_field:
            output_audio_field.setText(self.output_audio)

    def add_button(self, text, action, layout):
        button = QPushButton(text)
        button.clicked.connect(action)
        layout.addWidget(button)

    def add_file_field(self, label: str, button_label: str, field_name: str, dir: str, type: str,
                       layout: QVBoxLayout):
        """Adds a file input field with a label and browse button."""
        text_field_label = QLabel(label)
        text_field_label.setFixedWidth(self.side_ui_size)

        text_field_box = QLineEdit()
        text_field_box.setText(dir)
        text_field_box.setObjectName(field_name)

        text_field_button = QPushButton(button_label)
        text_field_button.setFixedWidth(self.side_ui_size)

        text_field_box.textChanged.connect(lambda text, name=field_name: self.update_variable(name, text))

        if type == 'input':
            text_field_button.clicked.connect(lambda: self.get_input_video(text_field_box, False))
        elif type == 'input2':
            text_field_button.clicked.connect(lambda: self.get_input_video(text_field_box, True))
        elif type == 'images':
            text_field_button.clicked.connect(lambda: self.get_image_file_dir(text_field_box))
        elif type == 'output':
            text_field_button.clicked.connect(lambda: self.get_output_video(text_field_box))
        elif type == 'audio':
            text_field_button.clicked.connect(lambda: self.get_output_audio(text_field_box))

        local_layout = QHBoxLayout()
        local_layout.addWidget(text_field_label)
        local_layout.addWidget(text_field_box)
        local_layout.addWidget(text_field_button)
        layout.addLayout(local_layout)

    def update_variable(self, name: str, value: str):
        """Update an instance variable dynamically from a field change."""
        setattr(self, name, value)

    def get_input_video(self, text_field: QLineEdit, is_second_file: bool):
        """Opens a file dialog to select a video file and updates the text field.

        Also updates video properties and spinbox ranges.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select an Existing File")
        if file_path:
            if not is_second_file:
                self.input_video = file_path
            else:
                self.input_video_2 = file_path
            text_field.setText(file_path)
            self.update_video_frame_rate(self.input_video)
            self.trim_page.update_trim_spinbox_ranges()
            return file_path

    def get_image_file_dir(self, text_field: QLineEdit):
        """
        Opens a directory dialog to select an existing directory where images should be.
        """
        files = QFileDialog.getExistingDirectory(self, "Chose the Directory with all Images")
        if files:
            self.images_dir = files
            text_field.setText(files)
            return files

    def get_output_video(self, text_field):
        """
        Opens a save file dialog for the output video, ensuring the file does not already exist.
        """
        while True:
            file_path, _ = QFileDialog.getSaveFileName(self, "Create a NON EXISTING Output File Name")
            if not file_path:
                return None
            if not os.path.exists(file_path):
                self.output_video = file_path
                text_field.setText(file_path)
                return file_path
            else:
                QMessageBox.warning(self, "File Exists", "Please select a new file name that does not already exist.")

    def get_output_audio(self, text_field: QLineEdit):
        """
        Opens a save file dialog for the output audio file.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Output Audio File")
        if file_path:
            self.output_audio = file_path
            text_field.setText(self.output_audio)
            return file_path

    def update_video_frame_rate(self, filename):
        """Uses ffprobe to extract the frame rate and duration of the given video file.

        Updates instance variables self.frame_rate and self.video_duration.
        If extraction fails, prints an error and leaves previous values unchanged.
        """
        try:
            # Get frame rate from ffprobe output
            fps_result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "v",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    "-show_entries", "stream=r_frame_rate",
                    filename,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            fps_string = fps_result.stdout.decode('utf-8').strip().split('/')
            fps = math.ceil(float(fps_string[0]) / float(fps_string[1]))
            # making sure fps cant be below 1
            if fps <= 0:
                fps = 1

            # Get duration from ffprobe output
            duration_result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    filename,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            duration = float(duration_result.stdout.decode('utf-8').strip())
            self.frame_rate, self.video_duration = int(fps), int(duration)
        except Exception as e:
            print(f"Error getting video info: {e}")

    def has_audio(self, video_path):
        result = subprocess.run(
            ["ffprobe", "-i", video_path, "-show_streams", "-select_streams", "a", "-loglevel", "error"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return bool(result.stdout)


class Compress10MBPage(QWidget):
    """Page for compressing a video to fit a 10 MB size (Discord upload limit)."""
    def __init__(self, main_window):
        """
        Set up UI for compress to 10MB page.
        """
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_window.add_file_field('Input Video: ', 'Browse', 'input_video_field',
                                        main_window.input_video, 'input', layout)
        self.main_window.add_file_field('Output Video: ', 'Browse', 'output_video_field',
                                        main_window.output_video, 'output', layout)
        self.main_window.add_button("Create Video", self.create_video, layout)

        self.setLayout(layout)

    def create_video(self):
        """Compresses the input video to fit within 10 MB using two-pass encoding.

        - Uses 9 MB as a target to avoid overshooting.
        - Calculates video bitrate based on video duration and a fixed audio bitrate.
        - Runs ffmpeg in two passes for best quality.
        - Displays user messages for errors or success.
        """
        input_ext = pathlib.Path(self.main_window.input_video).suffix.lower()
        output_ext = pathlib.Path(self.main_window.output_video).suffix.lower()

        if input_ext not in VIDEO_EXTENSIONS or output_ext not in VIDEO_EXTENSIONS:
            MessageUtils.invalid_video(self)
            return

        duration = self.main_window.video_duration
        target_size_bytes = 9 * 1024 * 1024
        audio_bitrate = 128 * 1024  # 128 kbps for audio
        # Calculate video bitrate to fit target file size (in bits per second)
        video_bitrate = int((target_size_bytes * 8 - audio_bitrate * duration) / duration)
        # Use /dev/null (Linux/Mac) or NUL (Windows) as the output for the first ffmpeg pass.
        null_file = 'NUL' if os.name == 'nt' else '/dev/nul'

        print(f"[DEBUG] Compressing {self.main_window.input_video} to {self.main_window.output_video} at {video_bitrate} bps.")

        # First pass: analyze video only (no audio)
        first_pass_cmd = [
            'ffmpeg', '-y', '-i', self.main_window.input_video,
            '-c:v', 'libx264', '-b:v', str(video_bitrate),
            '-pass', '1', '-an', '-f', 'null', null_file
        ]
        try:
            subprocess.run(first_pass_cmd, check=True)
        except subprocess.CalledProcessError as e:
            MessageUtils.operation_failed(self, f"First pass failed: {e}")
            return

        # Second pass: actual encoding with audio
        second_pass_cmd = [
            'ffmpeg', '-i', self.main_window.input_video,
            '-c:v', 'libx264', '-b:v', str(video_bitrate),
            '-pass', '2', '-c:a', 'aac', '-b:a', '128k',
            self.main_window.output_video
        ]
        try:
            subprocess.run(second_pass_cmd, check=True)
            MessageUtils.operation_success(self, "Compression completed successfully.")
        except subprocess.CalledProcessError as e:
            MessageUtils.operation_failed(self, f"Second pass failed: {e}")

        # Removes temporary log files
        finally:
            for f in ("ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"):
                if os.path.exists(f):
                    os.remove(f)


class TrimPage(QWidget):
    """Page for trimming/cutting a video by specifying start and end times.

    Provides spinboxes for minutes, seconds, and frames for precise selection.
    """
    def __init__(self, main_window):
        """
        Set up UI for trim page.
        """
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_window.add_file_field('Input Video: ', 'Browse', 'input_video_field',
                                        main_window.input_video, 'input', layout)
        self.main_window.add_file_field('Output Video: ', 'Browse', 'output_video_field',
                                        main_window.output_video, 'output', layout)
        self.trim_time = self.add_trim_inputs(layout)
        self.main_window.add_button("Create Video", self.create_video, layout)

        self.setLayout(layout)

    def add_label(self, text, layout):
        label = QLabel(text)
        layout.addWidget(label)
        return label

    def add_trim_inputs(self, layout):
        max_frames = self.main_window.video_duration
        self.max_min = self.main_window.video_duration
        max_minutes = self.max_min // 60
        max_seconds = self.max_min % 60

        start_layout = QVBoxLayout()
        self.add_label("Start Time:", start_layout)
        # QDoubleSpinBox for start time in seconds (decimal)
        self.start_input = QDoubleSpinBox()
        self.start_input.setDecimals(2)
        self.start_input.setSingleStep(0.25)
        self.start_input.setRange(0, self.main_window.video_duration)

        self.start_m = QSpinBox()
        self.start_m.setRange(0, max_minutes)
        self.start_s = QSpinBox()
        self.start_s.setRange(0, max_seconds)
        self.start_f = QSpinBox()
        self.start_f.setRange(0, self.main_window.frame_rate - 1)

        spin_layout = QHBoxLayout()
        spin_layout.addWidget(QLabel("M:"))
        spin_layout.addWidget(self.start_m, stretch=1)
        spin_layout.addWidget(QLabel("S:"))
        spin_layout.addWidget(self.start_s, stretch=1)
        spin_layout.addWidget(QLabel("F:"))
        spin_layout.addWidget(self.start_f, stretch=1)

        start_layout.addLayout(spin_layout)
        layout.addLayout(start_layout)

        end_layout = QVBoxLayout()
        self.add_label("End Time:", end_layout)

        self.end_input = QDoubleSpinBox()
        self.end_input.setDecimals(2)
        self.end_input.setSingleStep(0.25)
        self.end_input.setRange(0, self.main_window.video_duration)

        self.end_m = QSpinBox()
        self.end_m.setRange(0, max_minutes)
        self.end_s = QSpinBox()
        self.end_s.setRange(0, max_seconds)
        self.end_f = QSpinBox()
        self.end_f.setRange(0, self.main_window.frame_rate - 1)

        spin_layout2 = QHBoxLayout()
        spin_layout2.addWidget(QLabel("M:"))
        spin_layout2.addWidget(self.end_m, stretch=1)
        spin_layout2.addWidget(QLabel("S:"))
        spin_layout2.addWidget(self.end_s, stretch=1)
        spin_layout2.addWidget(QLabel("F:"))
        spin_layout2.addWidget(self.end_f, stretch=1)

        end_layout.addLayout(spin_layout2)
        layout.addLayout(end_layout)

    def update_trim_spinbox_ranges(self):
        """Updates the ranges of the trim time spinboxes based on the current video duration and frame rate.

        Should be called whenever a new video is loaded.
        """
        duration = self.main_window.video_duration
        frame_rate = self.main_window.frame_rate
        max_minutes = int(duration) // 60

        # Minutes: 0 to max_minutes
        self.start_m.setRange(0, max_minutes)
        self.end_m.setRange(0, max_minutes)

        # Seconds: always 0 to 59 (not limited by duration)
        self.start_s.setRange(0, 59)
        self.end_s.setRange(0, 59)

        # Frames: always 0 to (frame_rate - 1)
        self.start_f.setRange(0, frame_rate - 1)
        self.end_f.setRange(0, frame_rate - 1)

        # The total time in seconds (with minutes/seconds/frames) must be checked on use
        self.start_input.setRange(0, duration)
        self.end_input.setRange(0, duration)

        print(f"[DEBUG] Updated trim spinbox ranges: minutes 0-{max_minutes}, seconds 0-59, frames 0-{frame_rate - 1}")

    def get_start_and_end_trim(self):
        sm, ss, sf = self.start_m.value(), self.start_s.value(), self.start_f.value()
        em, es, ef = self.end_m.value(), self.end_s.value(), self.end_f.value()

        start = sm * 60 + ss + sf / self.main_window.frame_rate
        end = em * 60 + es + ef / self.main_window.frame_rate

        print(f"[DEBUG] Trim start: {start}s, end: {end}s")
        return start, end

    def create_video(self):
        """Runs ffmpeg to trim the video according to the selected start and end times."""
        input_ext = pathlib.Path(self.main_window.input_video).suffix.lower()
        output_ext = pathlib.Path(self.main_window.output_video).suffix.lower()

        if input_ext not in VIDEO_EXTENSIONS or output_ext not in VIDEO_EXTENSIONS:
            MessageUtils.invalid_video(self)
            return

        start, end = self.get_start_and_end_trim()
        if start >= end:
            MessageUtils.operation_failed(self, "Start time must be less than end time.")
            return

        # Build ffmpeg command for trimming
        cmd = ["ffmpeg", "-i", self.main_window.input_video]
        if start != 0:
            cmd += ["-ss", str(start)]
        if end != 0:
            cmd += ["-to", str(end)]
        cmd += ["-c:v", "libx264"]
        if self.main_window.has_audio(self.main_window.input_video):
            cmd += ["-c:a", "aac"]
        cmd += [self.main_window.output_video]

        print(f"[DEBUG] Running ffmpeg command: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            MessageUtils.operation_success(self, "Trim completed successfully.")
        except subprocess.CalledProcessError as e:
            MessageUtils.operation_failed(self, e.stderr.decode())


class SpeedPage(QWidget):
    """Page for changing the playback speed of a video.

    Provides a slider and input box for selecting speed multiplier.
    """
    def __init__(self, main_window):
        """
        Set up UI for speed page.
        """
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_window.add_file_field('Input Video: ', 'Browse', 'input_video_field',
                                        main_window.input_video, 'input', layout)
        self.main_window.add_file_field('Output Video: ', 'Browse', 'output_video_field',
                                        main_window.output_video, 'output', layout)
        self.speed = 1
        self.add_speed_slider_field("Speed: ", 'speed', layout)
        self.main_window.add_button("Create Video", self.create_video, layout)

        self.setLayout(layout)

    def add_speed_slider_field(self, label: str, field_name: str, layout: QVBoxLayout):
        """Adds a label, slider and input box to control video speed."""
        min, base, max = 1, 100, 1000
        modifier_field_label = QLabel(label)
        modifier_field_label.setFixedSize(self.main_window.side_ui_size, 24)
        modifier_field_slider = QSlider(Qt.Orientation.Horizontal)
        modifier_field_slider.setRange(min, max)
        modifier_field_slider.setValue(100)
        modifier_field_box = QLineEdit("1.0")
        modifier_field_box.setFixedWidth(self.main_window.side_ui_size)
        setattr(self, f"{field_name}_slider", modifier_field_slider)
        setattr(self, f"{field_name}_field", modifier_field_box)

        def slider_changed(value):
            speed = value / base
            modifier_field_box.setText(f"{speed:.2f}")
            self.speed = speed

        def box_changed():
            try:
                speed = float(modifier_field_box.text())
                value = int(speed * base)
                self.speed = speed
                if min > value:
                    pass
                elif min <= value <= max:
                    modifier_field_slider.setValue(value)
            except ValueError:
                pass

        modifier_field_slider.valueChanged.connect(slider_changed)
        modifier_field_box.editingFinished.connect(box_changed)

        local_layout = QHBoxLayout()
        local_layout.addWidget(modifier_field_label)
        local_layout.addWidget(modifier_field_slider)
        local_layout.addWidget(modifier_field_box)
        layout.addLayout(local_layout)
        return modifier_field_box.text()

    def create_video(self):
        """Runs ffmpeg to change the video speed using setpts filter."""
        input_ext = pathlib.Path(self.main_window.input_video).suffix.lower()
        output_ext = pathlib.Path(self.main_window.output_video).suffix.lower()
        if input_ext not in VIDEO_EXTENSIONS or output_ext not in VIDEO_EXTENSIONS:
            MessageUtils.invalid_video(self)
            return

        speed = 1 / self.speed
        cmd = [
            "ffmpeg", "-y", "-i", self.main_window.input_video,
            "-filter_complex", f"[0:v]setpts={speed}*PTS[v]",
            "-map", "[v]", "-c:v", "libx264", self.main_window.output_video
        ]

        print(f"[DEBUG] Running ffmpeg command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            MessageUtils.operation_success(self, "Speed change completed successfully.")
        except subprocess.CalledProcessError as e:
            MessageUtils.operation_failed(self, str(e))


class CatPage(QWidget):
    """Page for concatenating (combining) two videos into one."""
    def __init__(self, main_window):
        """Set up UI for cat page."""
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_window.add_file_field('Input Video 1: ', 'Browse', 'input_video_field',
                                        main_window.input_video, 'input', layout)
        self.main_window.add_file_field('Input Video 2: ', 'Browse', 'input_video_field_2',
                                        main_window.input_video_2, 'input2', layout)
        self.main_window.add_file_field('Output Video: ', 'Browse', 'output_video_field',
                                        main_window.output_video, 'output', layout)
        self.main_window.add_button("Create Video", self.create_video, layout)

        self.setLayout(layout)

    def create_video(self):
        """Runs ffmpeg to concatenate two video files using the concat filter."""
        input_ext = pathlib.Path(self.main_window.input_video).suffix.lower()
        input_2_ext = pathlib.Path(self.main_window.input_video_2).suffix.lower()
        output_ext = pathlib.Path(self.main_window.output_video).suffix.lower()
        if (input_ext not in VIDEO_EXTENSIONS or
            input_2_ext not in VIDEO_EXTENSIONS or
            output_ext not in VIDEO_EXTENSIONS):
            MessageUtils.invalid_video(self)
            return

        cmd = [
            "ffmpeg",
            "-i", self.main_window.input_video,
            "-i", self.main_window.input_video_2,
            "-filter_complex", "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]",
            "-map", "[outv]",
            "-map", "[outa]",
            self.main_window.output_video
        ]

        print(f"[DEBUG] Running ffmpeg command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            MessageUtils.operation_success(self, "Concatenation completed successfully.")
        except subprocess.CalledProcessError as e:
            MessageUtils.operation_failed(self, str(e))


class ImageToVideoPage(QWidget):
    """Page for creating a video from a sequence of images.

    Renames images to a sequential format and runs ffmpeg to encode them.
    """
    def __init__(self, main_window):
        """Set up UI for image-to-video page."""
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_window.add_file_field('Images Dir: ', 'Browse', 'images_dir_field',
                                        main_window.images_dir, 'images', layout)
        self.main_window.add_file_field('Output Video: ', 'Browse', 'output_dir_field',
                                        main_window.output_video, 'output', layout)
        self.main_window.add_button("Create Video", self.create_video, layout)

        self.setLayout(layout)

    def create_video(self):
        """Runs ffmpeg to create a video from a sequence of images in the selected directory.

        Calls fix_naming() to ensure images are named sequentially.
        Shows user warnings for invalid input and errors for failed processing.
        After successful creation, deletes the used image files.
        """
        output_ext = pathlib.Path(self.main_window.output_video).suffix.lower()

        # Validate input video extension
        if output_ext not in VIDEO_EXTENSIONS:
            MessageUtils.invalid_video(self)
            return

        self.fix_naming()

        # Build ffmpeg command for image sequence to video
        cmd = [
            "ffmpeg", "-framerate", "1",
            "-start_number", "1",
            "-i", os.path.join(self.main_window.images_dir, "img-%02d.jpg"),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease:eval=frame,pad=1920:1080:-1:-1:eval=frame",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", self.main_window.output_video
        ]
        print(f"[DEBUG] Running ffmpeg command: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            MessageUtils.operation_success(self, "Image to video conversion completed successfully.")

            # After successful video creation, delete the used images
            # Use glob to match the pattern img-??.jpg in the image directory
            images_dir = self.main_window.images_dir
            pattern = os.path.join(images_dir, "img-??.jpg")
            files_to_delete = glob.glob(pattern)

            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"[DEBUG] Deleted file: {file_path}")
                except Exception as e:
                    print(f"[DEBUG] Failed to delete {file_path}: {e}")
            if not files_to_delete:
                print("[DEBUG] No img-??.jpg files found to delete.")

        except subprocess.CalledProcessError as e:
            MessageUtils.operation_failed(self, str(e))

    def fix_naming(self):
        """Copies and renames all image files in the selected directory to a sequential format (img-01.jpg, img-02.jpg, ...).

        This ensures ffmpeg can process the images as a sequence.
        Does not overwrite existing files with the same name.
        """

        images = os.listdir(self.main_window.images_dir)
        num = 1
        for image in images:
            if pathlib.Path(image).suffix.lower() in IMAGE_EXTENSIONS:
                print(f"[DEBUG] Renaming {image} to img-{num:02d}.jpg")
                name = f'img-{num:02d}.jpg'
                shutil.copy(os.path.join(self.main_window.images_dir, image),
                            os.path.join(self.main_window.images_dir, name))
                num += 1


class ExtractSoundPage(QWidget):
    """Page for extracting audio from a video file and saving it in a selected format."""
    def __init__(self, main_window):
        """Set up UI for extract-audio page."""
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_window.add_file_field('Input Video: ', 'Browse', 'input_video_field',
                                        main_window.input_video, 'input', layout)
        self.main_window.add_file_field('Output Audio: ', 'Browse', 'output_audio_field',
                                        main_window.output_audio, 'audio', layout)
        self.main_window.add_button("Extract Audio", self.extract_audio, layout)

        self.setLayout(layout)

    def extract_audio(self):
        """Runs ffmpeg to extract audio from the input video file.

        Selects the codec based on output file extension.
        Shows user warnings for invalid input and errors for failed processing.
        """
        input_ext = pathlib.Path(self.main_window.input_video).suffix.lower()
        output_ext = pathlib.Path(self.main_window.output_audio).suffix.lower()
        if (input_ext not in VIDEO_EXTENSIONS or
            not self.main_window.has_audio(self.main_window.input_video) or
            output_ext not in AUDIO_EXTENSIONS):
            if input_ext not in VIDEO_EXTENSIONS:
                MessageUtils.invalid_video(self)
            elif output_ext not in AUDIO_EXTENSIONS:
                MessageUtils.invalid_audio(self)
            else:
                MessageUtils.no_audio_stream(self)
            return

        cmd = [
            "ffmpeg",
            "-i", self.main_window.input_video,
            "-map", "0:a",
            "-q:a", "0",
            "-acodec", AUDIO_CODEC_MAP[output_ext],
            self.main_window.output_audio
        ]
        print(f"[DEBUG] Running ffmpeg command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            MessageUtils.operation_success(self, "Audio extraction completed successfully.")
        except subprocess.CalledProcessError as e:
            MessageUtils.operation_failed(self, str(e))


if __name__ == "__main__":
    # Entry point for the application.
    app = QApplication(sys.argv)
    window = FFmpegGUI()
    window.show()
    sys.exit(app.exec())
