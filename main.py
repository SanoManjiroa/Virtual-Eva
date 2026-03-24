import os

import pygame
import sys
import time
import asyncio
import threading
import edge_tts
import speech_recognition as sr
import tempfile

# -------------------------------
# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Fullscreen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("EVA Cartoon Robot")

# -------------------------------
# Load EVA layers (keep original size)
body_img = pygame.image.load("eva_body.png").convert_alpha()
head_img = pygame.image.load("eva_head.png").convert_alpha()
left_arm_img = pygame.image.load("eva_left_arm.png").convert_alpha()
right_arm_img = pygame.image.load("eva_right_arm.png").convert_alpha()

# -------------------------------
# Positions for centered EVA
body_pos = [WIDTH//2 - body_img.get_width()//2, HEIGHT//2 - body_img.get_height()//2]
head_pos = [body_pos[0]+20 + (body_img.get_width()//2 - head_img.get_width()//2), body_pos[1] - head_img.get_height() + 10]
left_arm_pos = [body_pos[0] - left_arm_img.get_width() + 20, body_pos[1] + 50]
right_arm_pos = [body_pos[0] + body_img.get_width() - 20, body_pos[1] + 50]

# -------------------------------
# Animation variables
float_direction = 1
float_offset = 0

# Voice
voice_played = False
start_time = time.time()

# -------------------------------
# TTS function

def speak_in_thread(text):
    # Create a temporary MP3 file for this speech
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_filename = tmp_file.name
    tmp_file.close()  # close so edge_tts can write to it

    async def tts_and_play():
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        await communicate.save(tmp_filename)  # save to temp file
        pygame.mixer.music.load(tmp_filename)  # load into pygame
        pygame.mixer.music.play()
        # Wait until finished playing then delete
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        try:
            os.remove(tmp_filename)
        except:
            pass

    threading.Thread(target=lambda: asyncio.run(tts_and_play()), daemon=True).start()
# -------------------------------
# Speech listening function
def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        with mic as source:
            print("EVA listening...")
            audio = recognizer.listen(source, phrase_time_limit=3)
        try:
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            if "hello" in text.lower():
                threading.Thread(target=speak_in_thread, args=("Hello! Nice to meet you Shukrona I love you too.",), daemon=True).start()
            if "good night" in text.lower():
                threading.Thread(target=speak_in_thread, args=("Sherali Nice to meet you . Yakshi ukhla ",), daemon=True).start()
            elif "how are you" in text.lower():
                threading.Thread(target=speak_in_thread, args=("I am fine, thank you!",), daemon=True).start()
        except:
            pass

# Start listening in a separate thread
threading.Thread(target=listen_and_respond, daemon=True).start()

# -------------------------------
# Main loop
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Floating head animation
    float_offset += float_direction * 20 * dt
    if float_offset > 5:
        float_direction = -1
    elif float_offset < -5:
        float_direction = 1

    # Draw EVA in center
    screen.blit(left_arm_img, left_arm_pos)
    screen.blit(right_arm_img, right_arm_pos)
    screen.blit(body_img, body_pos)
    screen.blit(head_img, (head_pos[0], head_pos[1] + float_offset))

    pygame.display.update()

    # Speak after 1 second
    if not voice_played and time.time() - start_time >= 1:
        threading.Thread(target=speak_in_thread, args=("Hello, I am Eva",), daemon=True).start()
        voice_played = True

pygame.quit()
sys.exit()