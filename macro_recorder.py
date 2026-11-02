import time
import threading
from pynput import mouse, keyboard

events = []
recording = False
playing = False
play_thread = None
start_time = 0

QUIT_KEY = keyboard.KeyCode.from_char('`')
HOTKEYS = {keyboard.Key.f9, keyboard.Key.f10, QUIT_KEY}


def on_move(x, y):
    if recording:
        events.append(("move", x, y, time.time() - start_time))


def on_click(x, y, button, pressed):
    if recording:
        action = "click_press" if pressed else "click_release"
        events.append((action, x, y, button, time.time() - start_time))


def on_scroll(x, y, dx, dy):
    if recording:
        events.append(("scroll", x, y, dx, dy, time.time() - start_time))


def on_key_press(key):
    if key == keyboard.Key.f9:
        toggle_recording()
        return
    if key == keyboard.Key.f10:
        toggle_playback()
        return
    if key == QUIT_KEY:
        print("\nQuitting...")
        return False

    if recording:
        events.append(("key_press", key, time.time() - start_time))


def on_key_release(key):
    if recording and key not in HOTKEYS:
        events.append(("key_release", key, time.time() - start_time))


def toggle_recording():
    global recording, start_time, events
    if recording:
        recording = False
        print(f"Recording stopped. {len(events)} events captured.")
    else:
        events = []
        start_time = time.time()
        recording = True
        print("Recording... press F9 to stop.")


def toggle_playback():
    global playing, play_thread
    if playing:
        playing = False
        print("Playback stopped.")
    else:
        if not events:
            print("Nothing recorded yet! Press F9 to record first.")
            return
        playing = True
        play_thread = threading.Thread(target=playback_loop, daemon=True)
        play_thread.start()


def playback_loop():
    global playing
    m = mouse.Controller()
    kb = keyboard.Controller()
    loop_count = 0

    while playing:
        loop_count += 1
        print(f"Playing loop #{loop_count}...")
        prev_time = 0

        for event in events:
            if not playing:
                return

            timestamp = event[-1]
            delay = timestamp - prev_time
            if delay > 0:
                time.sleep(delay)
            prev_time = timestamp

            try:
                if event[0] == "move":
                    m.position = (event[1], event[2])
                elif event[0] == "click_press":
                    m.position = (event[1], event[2])
                    m.press(event[3])
                elif event[0] == "click_release":
                    m.position = (event[1], event[2])
                    m.release(event[3])
                elif event[0] == "scroll":
                    m.position = (event[1], event[2])
                    m.scroll(event[3], event[4])
                elif event[0] == "key_press":
                    kb.press(event[1])
                elif event[0] == "key_release":
                    kb.release(event[1])
            except Exception:
                pass

        time.sleep(0.3)

    print("Playback ended.")


def main():
    print("=== Macro Recorder ===")
    print("Records: keyboard + mouse (movement, clicks, scroll)")
    print()
    print("F9  - Start/stop recording")
    print("F10 - Start/stop playback (loops)")
    print("`   - Quit (backtick key)")
    print()

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    mouse_listener.start()

    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as kb_listener:
        kb_listener.join()

    mouse_listener.stop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
    input("\nPress Enter to close...")
