# VoiceTyper 🎤

语音转文字输入工具，基于 SenseVoice (MLX) 本地识别，按一下 Option 键说话，松开自动输入到当前输入框。

> 📺 视频介绍：[语音输入法,巨快无比](https://www.bilibili.com/video/BV1YLEp6KECM/)

## 特性

- **MLX 加速**：Apple Silicon 原生推理，识别仅 0.1s
- **本地运行**：语音识别完全离线，无需联网
- **一键操作**：按右 Option 开始/停止录音
- **自动输入**：识别结果直接粘贴到当前焦点窗口
- **后台常驻**：Daemon 由 launchd 管理，开机自启

## 安装

```bash
# 克隆仓库
git clone https://github.com/js110/voice2text.git
cd voice2text

# 创建虚拟环境
python3.12 -m venv sensevoice-env
source sensevoice-env/bin/activate

# 安装依赖
pip install mlx-audio sounddevice soundfile pynput

# 注册 Daemon（开机自启）
cp com.voicetyper.daemon.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.voicetyper.daemon.plist
```

## 使用

```bash
# 启动
./start-voicetyper.sh

# 或双击 VoiceTyper.app
```

- 按 **右 Option** 开始录音
- 再按 **右 Option** 停止，文字自动输入
- **Ctrl+C** 退出客户端

## 架构

```
VoiceTyper.app          ← 双击启动客户端（静默后台）
├── voicetyper.py       ← 客户端（录音 + 键盘监听）
├── voicetyper_daemon.py ← Daemon（MLX 模型常驻 + 识别）
└── start-voicetyper.sh ← 启动脚本
```

## 系统要求

- macOS 12+
- Python 3.12+
- Apple Silicon (M1/M2/M3/M4)
- 辅助功能权限（系统设置 → 隐私与安全性 → 辅助功能）
