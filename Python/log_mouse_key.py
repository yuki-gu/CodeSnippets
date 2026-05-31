from pynput import mouse, keyboard
import time
import threading
import signal

stop_flag = threading.Event()
print_lock = threading.Lock()

last_event_time = time.perf_counter()

mouse_listener = None
keyboard_listener = None

# 長押しリピート防止用
pressed_keys = set()


def delta_ms():
    global last_event_time

    now = time.perf_counter()
    diff = int((now - last_event_time) * 1000)
    last_event_time = now
    return diff


def safe_print(text=""):
    with print_lock:
        print(text, flush=True)


def print_event(ms, action, detail=""):
    """
    出力形式:
    相対ms | (mouse or key) (種類) (down or up) | 詳細情報
    """
    if detail:
        safe_print(f"{ms:>8} | {action:<22} | {detail}")
    else:
        safe_print(f"{ms:>8} | {action:<22}")


# --------------------
# マウス
# move / scroll は無視
# --------------------

def mouse_button_name(button):
    if button == mouse.Button.left:
        return "left"
    if button == mouse.Button.right:
        return "right"
    if button == mouse.Button.middle:
        return "middle"

    return str(button).replace("Button.", "")


def on_click(x, y, button, pressed):
    ms = delta_ms()
    btn = mouse_button_name(button)
    state = "down" if pressed else "up"

    print_event(
        ms,
        f"mouse {btn} {state}",
        f"x={x}, y={y}"
    )


# --------------------
# キーボード
# --------------------

def key_to_id(key):
    return str(key)


def key_to_name(key):
    try:
        # 通常文字キー
        if key.char is not None:
            return key.char.upper()
    except AttributeError:
        pass

    # 特殊キー
    return str(key).replace("Key.", "").upper()


def on_press(key):
    key_id = key_to_id(key)

    # 長押しによる key_press 連打を無視
    if key_id in pressed_keys:
        return

    pressed_keys.add(key_id)

    ms = delta_ms()
    key_name = key_to_name(key)

    print_event(
        ms,
        f"key {key_name} down"
    )


def on_release(key):
    key_id = key_to_id(key)
    pressed_keys.discard(key_id)

    ms = delta_ms()
    key_name = key_to_name(key)

    print_event(
        ms,
        f"key {key_name} up"
    )


# --------------------
# 終了処理
# --------------------

def stop_recording():
    stop_flag.set()


def handle_sigint(signum, frame):
    stop_recording()


def main():
    global mouse_listener, keyboard_listener

    signal.signal(signal.SIGINT, handle_sigint)

    safe_print("入力記録を開始しました。終了するには Ctrl + C を押してください。")
    safe_print()
    safe_print(f"{'ms':>8} | {'event':<22} | detail")
    safe_print("-" * 50)

    mouse_listener = mouse.Listener(
        on_click=on_click
    )

    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )

    mouse_listener.start()
    keyboard_listener.start()

    try:
        while not stop_flag.is_set():
            time.sleep(0.1)

    except KeyboardInterrupt:
        stop_recording()

    finally:
        safe_print("-" * 50)
        safe_print("入力記録を終了しました。")

        if mouse_listener is not None:
            mouse_listener.stop()

        if keyboard_listener is not None:
            keyboard_listener.stop()

        if mouse_listener is not None:
            mouse_listener.join(timeout=1)

        if keyboard_listener is not None:
            keyboard_listener.join(timeout=1)


if __name__ == "__main__":
    main()
