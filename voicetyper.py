#!/usr/bin/env python3
"""
🎤 VoiceTyper — 语音转文字
按右Option开始录音，再按结束，自动输入到当前输入框
"""
import os
import sys
import json
import socket
import time
import struct
import threading
import subprocess
import numpy as np
from pynput import keyboard

SOCK_PATH = "/tmp/voicetyper.sock"
SAMPLE_RATE = 16000
CHANNELS = 1

is_recording = False
audio_buffer = []
audio_stream = None

# ─── Daemon 通信 ───
def send_to_daemon(wav_path):
    with open(wav_path, 'rb') as f:
        data = f.read()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCK_PATH)
    sock.sendall(struct.pack('>I', len(data)))
    sock.sendall(data)
    sock.shutdown(socket.SHUT_WR)
    resp = b''
    while True:
        chunk = sock.recv(4096)
        if not chunk: break
        resp += chunk
    sock.close()
    return json.loads(resp.decode('utf-8'))

def recognize(audio_data):
    import soundfile as sf
    sf.write("/tmp/voicetyper_client.wav", audio_data, SAMPLE_RATE)
    result = send_to_daemon("/tmp/voicetyper_client.wav")
    if "error" in result:
        print(f"  ⚠️ {result['error']}")
        return ""
    return result["text"]

# ─── 输入文字 ───
PASTE_CMD = [
    'osascript', '-e',
    'tell application "System Events" to keystroke "v" using command down'
]

def type_text(text):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.communicate(text.encode('utf-8'))
    time.sleep(0.1)
    subprocess.run(PASTE_CMD, timeout=5)

# ─── 录音 ───
def audio_callback(indata, frames, time_info, status):
    if is_recording:
        audio_buffer.append(indata.copy())

def start_audio():
    global audio_stream
    import sounddevice as sd
    audio_stream = sd.InputStream(
        samplerate=SAMPLE_RATE, channels=CHANNELS,
        dtype='float32', callback=audio_callback
    )
    audio_stream.start()

def stop_audio():
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
        audio_stream = None

# ─── 切换录音 ───
def toggle_recording():
    global is_recording, audio_buffer

    if not is_recording:
        is_recording = True
        audio_buffer = []
        start_audio()
        sys.stdout.write("\r🔴 录音中...")
        sys.stdout.flush()
    else:
        is_recording = False
        stop_audio()

        if not audio_buffer:
            print("\r⚠️ 没录到声音          ")
            return

        audio = np.concatenate(audio_buffer, axis=0).flatten()
        if len(audio) / SAMPLE_RATE < 0.3:
            print("\r⚠️ 太短了              ")
            return

        sys.stdout.write("\r⏳ 识别中...")
        sys.stdout.flush()

        t0 = time.time()
        text = recognize(audio)
        elapsed = time.time() - t0

        if text:
            print(f"\r📝 {text}  ({elapsed:.1f}s)")
            type_text(text)
        else:
            print("\r⚠️ 未识别到语音        ")

# ─── 主程序 ───
def main():
    if not os.path.exists(SOCK_PATH):
        print("❌ Daemon 未启动，请先运行 start-voicetyper.sh")
        sys.exit(1)

    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCK_PATH)
        s.close()
    except:
        print("❌ 无法连接 Daemon")
        sys.exit(1)

    print("🎤 VoiceTyper 就绪  按右Option录音/停止  Ctrl+C退出")

    def on_press(key):
        if key == keyboard.Key.alt_r:
            toggle_recording()

    with keyboard.Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            stop_audio()
            print("\n👋")

if __name__ == "__main__":
    main()
