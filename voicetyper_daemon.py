#!/usr/bin/env python3
"""
🎤 VoiceTyper Daemon — MLX 加速版
模型只加载一次，加载 1.6s，识别 0.1s
"""
import os
import sys
import json
import socket
import time
import re
import threading
import subprocess

SOCK_PATH = "/tmp/voicetyper.sock"

# ─── 全局 ───
model = None

def load_model():
    global model
    sys.stdout.write("⏳ 加载 MLX SenseVoice...")
    sys.stdout.flush()
    t0 = time.time()
    from mlx_audio.stt.generate import load_model as _load, generate_transcription
    model = _load('mlx-community/SenseVoiceSmall')
    # 预热一次
    dummy = '/Users/jiangsheng/.cache/modelscope/hub/models/iic/SenseVoiceSmall/example/zh.mp3'
    if os.path.exists(dummy):
        generate_transcription(model=model, audio=dummy, language='zh', use_itn=True, output_path='/tmp/voicetyper_warmup', format='txt')
    print(f" ✅ {time.time()-t0:.1f}s")

def recognize(audio_path):
    from mlx_audio.stt.generate import generate_transcription
    result = generate_transcription(model=model, audio=audio_path, language='zh', use_itn=True, output_path='/tmp/voicetyper_out', format='txt')
    return result.text

def handle_client(conn):
    try:
        size_data = b''
        while len(size_data) < 4:
            chunk = conn.recv(4 - len(size_data))
            if not chunk: return
            size_data += chunk
        size = int.from_bytes(size_data, 'big')

        data = b''
        while len(data) < size:
            chunk = conn.recv(min(size - len(data), 65536))
            if not chunk: break
            data += chunk

        tmp_path = "/tmp/voicetyper_daemon.wav"
        with open(tmp_path, 'wb') as f:
            f.write(data)

        t0 = time.time()
        text = recognize(tmp_path)
        elapsed = time.time() - t0

        resp = json.dumps({"text": text, "time": round(elapsed, 2)})
        conn.sendall(resp.encode('utf-8'))
    except Exception as e:
        resp = json.dumps({"error": str(e)})
        try: conn.sendall(resp.encode('utf-8'))
        except: pass
    finally:
        conn.close()

def main():
    load_model()

    if os.path.exists(SOCK_PATH):
        os.unlink(SOCK_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCK_PATH)
    server.listen(5)
    print(f"🎤 Daemon 就绪 (socket: {SOCK_PATH})\n")

    try:
        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
    except KeyboardInterrupt:
        print("\n👋 Daemon 退出")
    finally:
        server.close()
        if os.path.exists(SOCK_PATH):
            os.unlink(SOCK_PATH)

if __name__ == "__main__":
    main()
