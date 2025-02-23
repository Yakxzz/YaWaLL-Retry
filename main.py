from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
import requests
import os
import platform

# Set fixed window size to 360x640
Window.size = (360, 640)
Window.borderless = True  # Ensures no resizing or zooming

class WallpaperApp(App):
    def build(self):
        # Check if the platform is Android
        if platform.system() == "Android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        #self.title = "YaWall Trial"
        self.wallpapers = [
            {"name": "Black Headphone", "url": "https://wallpaper.forfun.com/fetch/b1/b10c2b22fc83644699ec4822d102da6b.jpeg?h=900&r=0.5", "tags": ["Aesthetic Music", "Music", "Aesthetic"]},
            {"name": "Glass Guitar", "url": "https://wallpaper.forfun.com/fetch/0e/0ec93d50b4a57269969034140b8fdbde.jpeg?h=900&r=0.5", "tags": ["guitar", "glass"]},
            {"name": "Moon Art", "url": "https://wallpaper.forfun.com/fetch/f6/f639851874060b429f9049beb1cc6149.jpeg?h=900&r=0.5", "tags": ["aesthetic moon", "moon"]},
            {"name": "Flight Art", "url": "https://wallpaper.forfun.com/fetch/5e/5e7a7bf446d1af63d6f94808f5b38374.jpeg?h=900&r=0.5", "tags": ["Flight", "Aeroplane", "Aesthetic", "Colour Art"]},
            {"name": "Moon View", "url": "https://wallpaper.forfun.com/fetch/55/55a75bd94ac9b2cf880285e04f5a4b27.jpeg?h=900&r=0.5", "tags": ["Moon", "Sunset", "Aesthetic Moon", "Aesthetic"]},
            {"name": "Cloud House", "url": "https://wallpaper.forfun.com/fetch/5d/5d3fc070d749acfeb8c707d4460653f5.jpeg?h=900&r=0.5", "tags": ["House", "Sunset House", "Aesthetic House", "Clouds"]},
            ]
        self.uploaded_wallpapers = []  # List for uploaded wallpapers
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.main_screen = self.main_layout()  # Save the main layout as a separate widget
        self.layout.add_widget(self.main_screen)  # Add the main screen to the layout initially
        return self.layout

    def safe_async_image(self, source, **kwargs):
        try:
            return AsyncImage(source=source, **kwargs)
        except Exception as e:
            print(f"Error loading image {source}: {e}")
            return Label(text="Image not available", size_hint_y=None, height=250)
        
    def main_layout(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # App Title and Info Button
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.title_label = Label(text="Wallpapers by Yaksh", font_name="DejaVuSans", font_size=20, bold=True, color=(1, 1, 1, 1), halign='left')
        info_button = Button(text="ℹ", font_name="DejaVuSans", size_hint=(None, None), size=(50, 50), background_color=(0.1, 0.5, 1, 1))
        info_button.bind(on_release=self.open_info_page)  # Binding the button to open_info_page method
        title_layout.add_widget(self.title_label)
        title_layout.add_widget(info_button)
        layout.add_widget(title_layout)

        # Search Bar (without emoji)
        self.search_box = TextInput(hint_text="Search Wallpapers", font_name="DejaVuSans", size_hint_y=None, height=50, font_size=16, background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1), padding=[10, 10, 10, 10])
        self.search_box.bind(text=self.update_wallpapers)
        layout.add_widget(self.search_box)

        # Scrollable Grid Layout for Wallpapers
        self.scroll_view = ScrollView()
        self.grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll_view.add_widget(self.grid)
        layout.add_widget(self.scroll_view)

        self.update_wallpapers()
        return layout

    def update_wallpapers(self, *args):
        self.grid.clear_widgets()
        query = self.search_box.text.lower()
        found = False

        # Add predefined wallpapers
        for wp in self.wallpapers:
            all_tags = [wp["name"].lower()] + [tag.lower() for tag in wp.get("tags", [])]
            if any(query in tag for tag in all_tags):
                found = True
                wp_container = BoxLayout(orientation='vertical', size_hint_y=None, height=300, padding=5, spacing=5)
                img = AsyncImage(source=wp["url"], size_hint_y=None, height=250)
                btn = Button(text=wp["name"], font_name="DejaVuSans", size_hint_y=None, height=30, background_color=(0.1, 0.5, 1, 1), color=(1, 1, 1, 1), font_size=12)
                btn.bind(on_release=self.create_open_details_callback(wp, "predefined"))
                wp_container.add_widget(img)
                wp_container.add_widget(btn)
                self.grid.add_widget(wp_container)

        # Add uploaded wallpapers
        for wp in self.uploaded_wallpapers:
            found = True
            wp_container = BoxLayout(orientation='vertical', size_hint_y=None, height=300, padding=5, spacing=5)
            img = AsyncImage(source=wp["url"], size_hint_y=None, height=250)
            btn = Button(text=wp["name"], font_name="DejaVuSans", size_hint_y=None, height=30, background_color=(0.1, 0.5, 1, 1), color=(1, 1, 1, 1), font_size=12)
            btn.bind(on_release=self.create_open_details_callback(wp, "uploaded"))
            wp_container.add_widget(img)
            wp_container.add_widget(btn)
            self.grid.add_widget(wp_container)

        if not found:
            self.grid.add_widget(Label(text="Oops! No Wallpaper Found.", font_name="DejaVuSans", font_size=20, color=(1, 1, 1, 1), size_hint_y=None, height=50))

    def create_open_details_callback(self, wp, source):
        def callback(instance):
            self.open_wallpaper_details(wp, source)
        return callback

    def open_wallpaper_details(self, wp, source):
        self.layout.clear_widgets()
        img = AsyncImage(source=wp["url"], size_hint_y=None, height=480)
        name_label = Label(text=wp["name"], font_name="DejaVuSans", font_size=18, color=(1, 1, 1, 1))

        # Download and Apply buttons
        self.download_btn = Button(text="⬇ Download", font_name="DejaVuSans", size_hint_y=None, height=50, background_color=(0, 0.8, 0.4, 1), color=(1, 1, 1, 1))
        self.apply_btn = Button(text="Apply", font_name="DejaVuSans", size_hint_y=None, height=50, background_color=(0.8, 0.4, 0, 1), color=(1, 1, 1, 1))

        back_btn = Button(text="Back", font_name="DejaVuSans", size_hint_y=None, height=50, background_color=(1, 0, 0, 1), color=(1, 1, 1, 1))
        back_btn.bind(on_release=self.back_to_main)

        # Check if wallpaper already exists
        file_path = os.path.join(os.getcwd(), wp["name"] + ".jpg")
        if os.path.exists(file_path):
            self.download_btn.disabled = True
            self.download_btn.text = "Wallpaper Already Exists"

        # Bind buttons to their respective functions
        self.download_btn.bind(on_release=self.download_wallpaper(wp, source))
        self.apply_btn.bind(on_release=self.apply_wallpaper)

        self.layout.add_widget(img)
        self.layout.add_widget(name_label)
        self.layout.add_widget(self.download_btn)
        self.layout.add_widget(self.apply_btn)
        self.layout.add_widget(back_btn)

    def download_wallpaper(self, wp, source):
        def callback(instance):
            try:
                # Disable the download button after it's clicked
                self.download_btn.disabled = True
                self.download_btn.text = "Downloaded..."
                # Download the wallpaper and save it to the local storage
                img_data = requests.get(wp["url"]).content
                file_name = wp["name"] + ".jpg"
                file_path = os.path.join(os.getcwd(), file_name)

                # Check if file already exists, append a number to the filename if so
                counter = 1
                while os.path.exists(file_path):
                    file_path = os.path.join(os.getcwd(), f"{wp['name']}_{counter}.jpg")
                    counter += 1

                with open(file_path, 'wb') as f:
                    f.write(img_data)
                print(f"Wallpaper downloaded to {file_path}")

                # Provide feedback to the user
                self.show_message(f"Wallpaper downloaded!", "downloaded")
                Clock.schedule_once(lambda dt: self.remove_message(), 5)  # Remove after 5 seconds
            except Exception as e:
                print(f"Error: {e}")
                self.show_message("Download failed. Please try again.", "failed")

        return callback

    def apply_wallpaper(self, instance):
        # Disable the apply button after it's clicked
        self.apply_btn.disabled = True
        self.apply_btn.text = "Error 404!"
        # Logic to apply the wallpaper (e.g., change background or set it as the wallpaper for the system)
        self.show_message("Error Occured!", "Error")
        Clock.schedule_once(lambda dt: self.remove_message(), 5)  # Remove after 5 seconds

    def back_to_main(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(self.main_screen)  # Use the saved main screen layout

    def open_info_page(self, instance):
        """This method is now defined to open the information page."""
        self.layout.clear_widgets()
        info_label = Label(text="Made by Yaksh\nVersion : 2.3.5", font_name="DejaVuSans", font_size=20, halign='center', valign='middle')
        back_btn = Button(text="Back", font_name="DejaVuSans", size_hint_y=None, height=50, background_color=(1, 0, 0, 1), color=(1, 1, 1, 1))
        back_btn.bind(on_release=self.back_to_main)

        self.layout.add_widget(info_label)
        self.layout.add_widget(back_btn)

    def show_message(self, message, status):
        msg_label = Label(text=message, font_name="DejaVuSans", font_size=16, color=(1, 1, 1, 1), size_hint_y=None, height=50)
        if status == "downloaded":
            msg_label.background_color = (0, 0.8, 0.4, 1)  # Green for success
        elif status == "failed":
            msg_label.background_color = (0.8, 0.4, 0, 1)  # Red for failure
        else:
            msg_label.background_color = (0.8, 0.8, 0, 1)  # Yellow for info
        self.layout.add_widget(msg_label)

    def remove_message(self):
        self.layout.clear_widgets()
        self.layout.add_widget(self.main_screen)

if __name__ == "__main__":
    try:
        WallpaperApp().run()
    except Exception as e:
        print(f"Error: {e}")