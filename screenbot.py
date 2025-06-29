import os
import time
import subprocess
import pyautogui
from pynput import mouse, keyboard
import pygetwindow as gw

SCREENSHOT_FOLDER = "screenshots_auto"
APP_PATH = "app.py"
WINDOW_TITLE_HINT = "Library"  # Change this to match your app window title
DELAY_BEFORE_CAPTURE = 0.2  # Wait before screenshot after event

# Setup
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)
screenshot_num = 1

def take_screenshot():
    global screenshot_num
    try:
        win = gw.getWindowsWithTitle(WINDOW_TITLE_HINT)[0]
        if not win.isMinimized:
            # Get window position and size
            left, top, width, height = win.left, win.top, win.width, win.height

            time.sleep(DELAY_BEFORE_CAPTURE)
            filepath = os.path.join(SCREENSHOT_FOLDER, f"event_{screenshot_num}.png")
            pyautogui.screenshot(filepath, region=(left, top, width, height))
            print(f"📸 Screenshot {screenshot_num} saved (window only)")
            screenshot_num += 1
        else:
            print("⚠️ Window is minimized, skipping screenshot")
    except IndexError:
        print(f"❌ No window found with title hint '{WINDOW_TITLE_HINT}'")


def on_click(x, y, button, pressed):
    if pressed:
        print(f"🖱️ Click at ({x}, {y})")
        take_screenshot()

def on_press(key):
    try:
        print(f"⌨️ Key pressed: {key.char}")
    except AttributeError:
        print(f"⌨️ Special key pressed: {key}")
    take_screenshot()

def focus_app_window():
    print("🎯 Focusing app window...")
    for _ in range(20):  # 10s timeout
        windows = gw.getWindowsWithTitle(WINDOW_TITLE_HINT)
        if windows:
            win = windows[0]
            win.restore()
            win.activate()
            return True
        time.sleep(0.5)
    print(f"❌ Could not focus window with title containing '{WINDOW_TITLE_HINT}'")
    return False

def main():
    # Launch the app
    print(f"🚀 Running: {APP_PATH}")
    subprocess.Popen(["python", APP_PATH])
    time.sleep(3)
    focus_app_window()

    print("🎥 Recording interactions (press ESC to stop)...")

    # Start listeners
    mouse_listener = mouse.Listener(on_click=on_click)
    # keyboard_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    # keyboard_listener.start()

    # Stop when ESC is pressed
    def stop_on_esc(key):
        if key == keyboard.Key.esc:
            print("🛑 ESC pressed. Exiting...")
            mouse_listener.stop()
            # keyboard_listener.stop()
            return False

    # Join the keyboard listener with ESC handler
    with keyboard.Listener(on_press=stop_on_esc) as esc_listener:
        esc_listener.join()

if __name__ == "__main__":
    main()
