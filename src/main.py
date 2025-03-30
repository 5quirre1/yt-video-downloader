"""
MIT License

Copyright (c) 2025 Squirrel Gay Acorn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

plz give credit if steal code
- Squirrel <3
"""

import os
import re
from typing import Optional
try:
    from pytubefix import YouTube
except ImportError:
    print("pytubefix not found, installing...")
    os.system("pip install pytubefix")
    from pytubefix import YouTube
try:
    from textual.app import App, ComposeResult
    from textual.containers import Container
    from textual.widgets import Button, Footer, Header, Input, Label, ProgressBar, Select, Static
    from textual.binding import Binding
    from textual import work
except ImportError:
    print("textual not found, installing...")
    os.system("pip install textual")
    from textual.app import App, ComposeResult
    from textual.containers import Container
    from textual.widgets import Button, Footer, Header, Input, Label, ProgressBar, Select, Static
    from textual.binding import Binding
    from textual import work
class Info(Static):
    pass
class App(App):
    CSS = """
    Screen {
        align: center middle;
        background: #0a192f;
        color: #8892b0;
    }
    #main-container {
        width: 90%;
        height: auto;
        border: thick #64ffda;
        padding: 2 4;
        background: #112240;
    }
    #title {
        text-align: center;
        background: #1e3a8a;
        color: #e0f2fe;
        padding: 1 2;
        margin-bottom: 1;
        width: 100%;
    }
    #url-input {
        width: 100%;
        margin-bottom: 1;
        background: #172a45;
        color: #e6f1ff;
        border: solid #64ffda;
    }
    Input:focus {
        border: solid #64ffda;
    }
    #format-select {
        margin-bottom: 1;
        width: 100%;
        background: #172a45;
        color: #e6f1ff;
        border: solid #64ffda;
    }
    Select > .option {
        background: #172a45;
        color: #e6f1ff;
    }
    Select > .option--highlighted {
        background: #1e3a8a;
    }
    Label {
        color: #ccd6f6;
    }
    #options-container {
        layout: horizontal;
        width: 100%;
        margin-top: 1;
        height: auto;
        align: center middle;
    }
    Button {
        margin: 1 2;
        background: #172a45;
        color: #64ffda;
        border: solid #64ffda;
    }
    Button:hover {
        background: #1e3a8a;
    }
    #download-info {
        margin-top: 1;
        height: auto;
        min-height: 2;
        width: 100%;
        border: solid #64ffda;
        padding: 1;
        background: #172a45;
        color: #ccd6f6;
    }
    #progress-container {
        margin-top: 1;
        height: auto;
        width: 100%;
    }
    ProgressBar {
        width: 100%;
        background: #172a45;
    }
    ProgressBar > .bar {
        background: #64ffda;
        color: #0a192f;
    }
    Header {
        background: #1e3a8a;
        color: #e6f1ff;
    }
    Header #title-text {
        color: #e6f1ff;
    }
    Footer {
        background: #1e3a8a;
        color: #e6f1ff;
    }
    """
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "download", "Download"),
        Binding("c", "clear", "Clear")
    ]
    def __init__(self):
        super().__init__()
        self.youtube: Optional[YouTube] = None
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
    def compose(self) -> ComposeResult:
        with Container(id="main-container"):
            yield Header()
            yield Label("yt video download", id="title")
            yield Label("enter url")
            yield Input(placeholder="https://www.youtube.com/watch?v=...", id="url-input")
            yield Label("select which to save as:")
            yield Select(
                [
                    ("Video (MP4)", "mp4"),
                    ("Audio Only (MP3)", "mp3"),
                ],
                value="mp4",
                id="format-select",
            )
            with Container(id="options-container"):
                yield Button("download", variant="primary", id="download-btn")
                yield Button("clear", variant="default", id="clear-btn")
            yield Info("ready :}", id="download-info")
            with Container(id="progress-container"):
                yield ProgressBar(total=100, id="download-progress")
            yield Footer()
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-btn":
            self.download()
        elif event.button.id == "clear-btn":
            self.clear()
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.download()
    def clear(self) -> None:
        self.query_one("#url-input", Input).value = ""
        self.query_one("#download-info", Info).update("ready :}")
        self.query_one("#download-progress", ProgressBar).update(progress=0)
        self.youtube = None
    def clean_url(self, url: str) -> str:
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            return f'https://www.youtube.com/watch?v={video_id}'
        return url
    @work(thread=True)
    def download(self) -> None:
        url = self.query_one("#url-input", Input).value
        format_value = self.query_one("#format-select", Select).value
        if not url:
            self.query_one("#download-info", Info).update("plz do real one")
            return
        cleaned_url = self.clean_url(url)
        self.query_one("#download-info", Info).update(f"getting info.. (cleaned URL)")
        try:
            self.youtube = YouTube(cleaned_url)
            def progress(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percentage = int(bytes_downloaded / total_size * 100)
                self.call_from_thread(
                    self.query_one("#download-progress", ProgressBar).update, 
                    progress=percentage
                )
            self.youtube.register_on_progress_callback(progress)
            title = self.youtube.title
            self.call_from_thread(
                self.query_one("#download-info", Info).update,
                f"Title: {title}\ngetting ready to download.."
            )
            if format_value == "mp4":
                stream = self.youtube.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
                if not stream:
                    stream = self.youtube.streams.filter(file_extension="mp4").order_by('resolution').desc().first()
                if stream:
                    file_path = stream.download(output_path=self.download_path)
                    self.call_from_thread(
                        self.query_one("#download-info", Info).update,
                        f"downloaded: \"{title}\"!\nsaved to: \"{file_path}\"!!"
                    )
                else:
                    self.call_from_thread(
                        self.query_one("#download-info", Info).update,
                        f"error: no stream found or smth for {title}"
                    )
            elif format_value == "mp3":
                stream = self.youtube.streams.filter(only_audio=True).order_by('abr').desc().first()
                if stream:
                    file_path = stream.download(output_path=self.download_path)
                    base, ext = os.path.splitext(file_path)
                    new_file_path = base + ".mp3"
                    os.rename(file_path, new_file_path)
                    self.call_from_thread(
                        self.query_one("#download-info", Info).update,
                        f"downloaded audio: {title}!\nsaved to: {new_file_path}!!"
                    )
                else:
                    self.call_from_thread(
                        self.query_one("#download-info", Info).update,
                        f"error: no stream found or smth for{title}"
                    )
        except Exception as e:
            self.call_from_thread(
                self.query_one("#download-info", Info).update,
                f"error: {str(e)}"
            )
def main():
    App().run()
if __name__ == "__main__":
    main()
