# FrameForge

[![Build Status](https://img.shields.io/github/actions/workflow/status/username/repo/ci.yml?branch=main)](https://github.com/MatsValgaeren/FrameForge/actions)
[![Coverage](https://img.shields.io/codecov/c/github/username/repo)](https://codecov.io/gh/username/repo)
[![Latest Release](https://img.shields.io/github/v/release/username/repo)](https://github.com/MatsValgaeren/FrameForge/releases)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/username/repo)](https://github.com/MatsValgaeren/FrameForge/issues)

</div>

<details>
<summary>Table of Contents</summary>

- [About](#about)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites-common-to-all-setups)
  - [Standalone App (Windows)](#standalone-app-windows)
  - [Python Script](#python-script)
- [Usage](#usage)
- [Roadmap & Contributing](#roadmap--contributing)
- [Credits](#credits)
- [License](#license)

</details>


## About

FrameForge is a python script you can use to do some quick video edits.

*Watch Demo Video Here: [YouTube Video](https://youtu.be/SPfN98WdyZ4)*


## Features

-   **10 MB / Discord Size:** Compress a video to ensure it is under 10 MB, making it suitable for Discord uploads.
-   **Trim / Cut Video:** Choose the start and end frames to extract a specific section of your video.
-   **Change Speed:** Adjust the playback speed of your video.
-   **Combine Videos:** Merge two videos into one.
-   **Image to Video:** Create a video collage from a selected image directory.
-   **Extract Audio:** Extract the audio track from a video file.


## Installation

### Prerequisites (Common to All Setups)

-   **FFmpeg:** Ensure FFmpeg is installed and added to your system's PATH. Download it from [FFmpeg Downloads](https://www.ffmpeg.org/download.html).

### Standalone App (Windows)

#### Setup

1.  [Prerequisites](#prerequisites-common-to-all-setups)
2.  Download the latest `FrameForge.exe` from [Releases](https://github.com/MatsValgaeren/FrameForge/releases).
3.  Run `FrameForge.exe`.

### Python Script

#### Requirements

-   [Prerequisites](#prerequisites-common-to-all-setups)
-   [PyQt6](https://pypi.org/project/PyQt6/)
-   Python 3.7+

#### Manual Setup

1.  Clone the repository:

    ```
    git clone https://github.com/MatsValgaeren/FrameForge.git
    ```
2.  Install dependencies:

    ```
    pip install -r requirements.txt
    ```
3.  Run the script:

    ```
    python frameforge.py
    ```


## Usage

1.  **Run FrameForge.exe** (or the Python script).
2.  **Choose one of the editing tabs**.
3.  **Select an input video file** (or an image directory for the Image-to-Video page).
4.  **Select an output video or audio file**.
5.  Change other settings.
6.  **Click "Create Video"** (or the appropriate action button) to process your file.

***Watch the Demo here: [YouTube Video](https://youtu.be/SPfN98WdyZ4)***


## Roadmap & Contributing

See the [open issues](https://github.com/MatsValgaeren/FrameForge/issues) to track planned features, known bugs, and ongoing work.

If you encounter any bugs or have feature requests, please submit them as new issues there.  Your feedback and contributions help improve FrameForge!


## Credits

-   Script by Mats Valgaeren
-   Powered by:
    -   [FFmpeg](https://github.com/FFmpeg/FFmpeg)
    -   [PyQt6](https://pypi.org/project/PyQt6/)


## License

[GNU General Public License v3.0](LICENSE)
