# FrameForge (Quick Simple Video Edits)

*A tool to quickly edit video files.*

*Watch Here: [YouTube Video](https://youtu.be/SPfN98WdyZ4)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Features

- **10 MB / Discord Size:** Compress a video to ensure it is under 10 MB, making it suitable for Discord uploads.
- **Trim / Cut Video:** Choose the start and end frames to extract a specific section of your video.
- **Change Speed:** Adjust the playback speed of your video.
- **Combine Videos:** Merge two videos into one.
- **Image to Video:** Create a video collage from a selected image directory.
- **Extract Audio:** Extract the audio track from a video file.

## Requirements

- [FFmpeg](https://www.ffmpeg.org/download.html) (must be installed and in your system PATH)
- [PyQt6](https://pypi.org/project/PyQt6/) (for Python script version)
- Python 3.7+ (for Python script version)

## Installation

### Standalone App (Windows)

1. Download the latest `FrameForge.exe` from [Releases](https://github.com/MatsValgaeren/FrameForge/releases).
2. Make sure [FFmpeg](https://www.ffmpeg.org/download.html) is installed and added to your PATH.
3. Run `FrameForge.exe`.

### Python Script

1. Clone the repository:
```
git clone https://github.com/MatsValgaeren/FrameForge.git
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Download and install [FFmpeg](https://www.ffmpeg.org/download.html) and add it to your PATH.
4. Run the script:
```
python frameforge.py
```
## Usage

1. **Run FrameForge.exe** (or the Python script).
2. **Choose one of the editing tabs**.
3. **Select an input video file** (or an image directory for the Image-to-Video page).
4. **Select an output video or audio file**.
5. Change other settings.
6. **Click "Create Video"** (or the appropriate action button) to process your file.

**Watch the Demo here:** [YouTube Video](https://youtu.be/SPfN98WdyZ4)

## Credits

- Script by Mats Valgaeren
- Powered by [FFmpeg](https://www.ffmpeg.org/)

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0)
