import cv2
import mediapipe as mp
import pyautogui
import time
import webbrowser
import pygetwindow as gw
from tkinter import *
from PIL import Image, ImageTk
import threading
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)
cap = cv2.VideoCapture(0)
last_action = ""
last_time = 0
action_cooldown = 1.5
def count_fingers(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []
    if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)
    for tip in tips_ids[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def detect_gesture(fingers):
    if fingers == [0, 1, 0, 0, 0]:
        return "playpause"
    elif fingers == [0, 1, 1, 0, 0]:
        return "nexttrack"
    elif fingers == [1, 1, 0, 0, 0]:
        return "volumeup"
    elif fingers == [1, 1, 1, 0, 0]:
        return "volumedown"
    elif fingers == [0, 0, 0, 0, 0]:
        return "mute"
    elif fingers == [1, 1, 1, 1, 1]:
        return "unmute"
    elif fingers == [0, 0, 1, 1, 0]:
        return "openyoutube"
    else:
        return "none"

def focus_browser():
    try:
        win = gw.getWindowsWithTitle('YouTube')[0]
        win.activate()
        time.sleep(0.2)
    except:
        pass

def perform_action(action):
    global last_action, last_time
    if time.time() - last_time < action_cooldown or action == last_action:
        return
    print(f">> Triggered: {action}")
    if action == "playpause":
        focus_browser()
        pyautogui.press('k')
    elif action == "nexttrack":
        pyautogui.press('l')
    elif action == "volumeup":
        pyautogui.press('volumeup')
    elif action == "volumedown":
        pyautogui.press('volumedown')
    elif action == "mute":
        pyautogui.press('m')
    elif action == "unmute":
        pyautogui.press('m')
    elif action == "openyoutube":
        webbrowser.open("https://www.youtube.com  ")

    last_action = action
    last_time = time.time()


root = Tk()
root.title("Gesture Controller")
root.geometry("350x300")
root.attributes("-topmost", True)

label = Label(root)
label.pack()

gesture_label = Label(root, text="Gesture: None", font=("Arial", 14))
gesture_label.pack()


def update_frame():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    gesture_state = "None"
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = count_fingers(hand_landmarks)
            gesture = detect_gesture(fingers)
            gesture_state = gesture
            perform_action(gesture)
    gesture_label.config(text=f"Gesture: {gesture_state}")

    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img_pil)
    label.imgtk = imgtk
    label.configure(image=imgtk)
    label.after(10, update_frame)
threading.Thread(target=update_frame, daemon=True).start()
root.mainloop()
cap.release()
cv2.destroyAllWindows()
