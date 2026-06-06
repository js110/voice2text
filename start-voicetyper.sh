#!/bin/bash
# VoiceTyper — 客户端启动器
# Daemon 由 launchd 自动管理，这里只启动客户端
PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$PROJ_DIR/sensevoice-env/bin/activate"

# 确保 Daemon 在跑
if ! launchctl list | grep -q com.voicetyper.daemon; then
    echo "🚀 启动 Daemon..."
    launchctl load ~/Library/LaunchAgents/com.voicetyper.daemon.plist
    sleep 3
fi

# 等 socket 就绪
for i in $(seq 1 30); do
    [ -S /tmp/voicetyper.sock ] && break
    sleep 1
done

if [ ! -S /tmp/voicetyper.sock ]; then
    echo "❌ Daemon 未就绪，查看日志: cat /tmp/voicetyper-daemon.log"
    exit 1
fi

# 启动客户端
python3 "$PROJ_DIR/voicetyper.py"
