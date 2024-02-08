from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from pytube import YouTube
import requests
from kivy.clock import Clock
import os

from android.permissions import Permission, check_permission, request_permissions
from jnius import autoclass

class YoutubeDownloaderApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Orange"

        self.layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        heading_label = MDLabel(text="Video Downloader", theme_text_color="Primary", halign="center", font_style="H4")
        self.layout.add_widget(heading_label)

        self.url_input = MDTextField(hint_text='Enter YouTube URL', multiline=False)

        self.quality_buttons_layout = MDGridLayout(cols=3, adaptive_height=True, spacing=30, padding=[170, 20, 170, 20])
        quality_options = ['144p', '240p', '360p', '480p', '720p', '1080p']

        for quality_option in quality_options:
            button = MDRaisedButton(text=quality_option, on_press=self.on_quality_button_press)
            self.quality_buttons_layout.add_widget(button)

        self.layout.add_widget(self.url_input)
        self.layout.add_widget(self.quality_buttons_layout)

        self.status_layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        self.status_label = MDLabel(text='', theme_text_color='Secondary', font_style='Body1')
        self.status_layout.add_widget(self.status_label)

        self.layout.add_widget(self.status_layout)

        if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        return self.layout

    def on_quality_button_press(self, instance):
        video_url = self.url_input.text
        video_quality = instance.text 

        if video_url:
            self.status_label.text = 'Downloading initiated...\nPlease wait a while...'
            Clock.schedule_once(lambda dt: self.start_download(video_url, video_quality), 0.1)

    def start_download(self, video_url, video_quality):
        try:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context

            if check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                yt = YouTube(video_url)

                stream = yt.streams.filter(res=video_quality, progressive=True).first()

                if stream:
                    Environment = autoclass('android.os.Environment')
                    downloads_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()

                    sanitized_title = "".join(c for c in yt.title if c.isalnum() or c in (' ', '.', '-', '_'))

                    download_path = os.path.join(downloads_dir, f"{sanitized_title}.mp4")

                    stream.download(output_path=downloads_dir, filename=sanitized_title+".mp4")
                    

                    self.update_status(f'Download complete: {yt.title}\nSaved at: {download_path}', 'Success')
                else:
                    if video_quality == "1080p":
                        stream = yt.streams.filter(res=video_quality).first()
                        if stream:
                            Environment = autoclass('android.os.Environment')
                            downloads_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
                            sanitized_title = "".join(c for c in yt.title if c.isalnum() or c in (' ', '.', '-', '_'))
                            download_path = os.path.join(downloads_dir, f"{sanitized_title}.webm")
                            stream.download(output_path=downloads_dir, filename=sanitized_title+".webm")
                            self.update_status(f'Download complete: {yt.title}\nSaved at: {download_path}', 'Success')
                        else:
                            self.update_status('The 1080p quality for the video is not available. Choose other Quality...', 'Error')
                    else:
                        self.update_status('The selected quality for the video is not available. Choose other Quality...', 'Error')

            else:
                self.update_status('Error: WRITE_EXTERNAL_STORAGE permission not granted', 'Error')

        except requests.exceptions.RequestException as e:
            self.update_status(f'Network error: {e}', 'Error')

        except Exception as e:
            self.update_status(f'Error: {e}', 'Error')

    def update_status(self, text, status_type):
        self.status_label.text = text
        if status_type == 'Success':
            self.status_label.theme_text_color = 'Primary'
        else:
            self.status_label.theme_text_color = 'Error'

if __name__ == '__main__':
    YoutubeDownloaderApp().run()
    
