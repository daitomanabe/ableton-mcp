# Ableton MCP 探索工具集

这个目录包含了用于探索和分析 Ableton Live API 的实用工具。

## 🛠️ 工具列表

### 1. `extract_api_from_push2.sh`
从官方 Push2 Remote Script 提取 API 使用模式。

**用途**: 发现 Ableton 官方使用了哪些 API

**使用方法**:
```bash
./extract_api_from_push2.sh
```

**输出**: `push2_api_usage.txt` - 包含所有 API 使用的列表

**要求**:
- macOS 上已安装 Ableton Live 12
- Push2 脚本在默认路径

---

### 2. `compare_versions.py`
对比不同版本的 Ableton Live API 变化。

**用途**: 发现 Live 11 -> Live 12 新增了什么功能

**使用方法**:
```bash
# 安装依赖
pip install requests

# 运行工具
python3 compare_versions.py
```

**功能**:
- 下载 Live 10/11/12 的 API XML 文档
- 对比版本间的差异
- 显示新增/移除的类和方法
- 查看特定类的完整 API

**交互式菜单**:
1. 对比两个版本
2. 查看特定类的 API
3. 退出

---

### 3. `api_explorer.py`
实时探索运行中的 Ableton Live API。

**用途**: 动态发现可用的 API 并分析覆盖率

**使用方法**:
```bash
# 1. 首先需要在 AbletonMCP_Remote_Script/__init__.py 中添加 explore_api 命令
#    (参见下面的"前置要求")

# 2. 运行探索器
python3 api_explorer.py
```

**功能**:
- 获取会话信息
- 探索 Song, Track, Clip, Device 等类的所有属性和方法
- 计算当前实现的覆盖率
- 列出未实现的功能

### 前置要求: 添加 explore_api 命令

在 `AbletonMCP_Remote_Script/__init__.py` 的 `_process_command` 方法中添加：

```python
elif command_type == "explore_api":
    category = params.get("category", "song")
    response["result"] = self._explore_api_category(category)
```

然后添加这个方法：

```python
def _explore_api_category(self, category):
    """探索特定类别的 API"""
    result = {
        "category": category,
        "attributes": [],
        "methods": [],
        "properties": []
    }

    obj = None
    if category == "song":
        obj = self._song
    elif category == "track":
        obj = self._song.tracks[0] if len(self._song.tracks) > 0 else None
    elif category == "clip":
        if len(self._song.tracks) > 0:
            track = self._song.tracks[0]
            for slot in track.clip_slots:
                if slot.has_clip:
                    obj = slot.clip
                    break
    elif category == "device":
        if len(self._song.tracks) > 0:
            track = self._song.tracks[0]
            obj = track.devices[0] if len(track.devices) > 0 else None
    elif category == "application":
        obj = self.application()
    elif category == "browser":
        obj = self.application().browser

    if obj is None:
        result["error"] = f"No {category} object available"
        return result

    # 探索所有属性
    for attr_name in dir(obj):
        if attr_name.startswith('_'):
            continue

        try:
            attr = getattr(obj, attr_name)
            attr_type = type(attr).__name__

            if callable(attr):
                result["methods"].append({
                    "name": attr_name,
                    "type": attr_type
                })
            else:
                try:
                    # 尝试获取值
                    value_repr = str(attr) if not isinstance(attr, (list, tuple)) or len(attr) < 10 else f"{type(attr).__name__}[{len(attr)}]"
                    result["properties"].append({
                        "name": attr_name,
                        "type": attr_type,
                        "value": value_repr[:100]  # 限制长度
                    })
                except:
                    result["properties"].append({
                        "name": attr_name,
                        "type": attr_type,
                        "value": "[not accessible]"
                    })
        except Exception as e:
            result["attributes"].append({
                "name": attr_name,
                "error": str(e)
            })

    return result
```

---

## 📋 典型工作流

### 场景 1: 我想知道 Push2 使用了哪些 API

```bash
# 1. 提取 Push2 使用的 API
./extract_api_from_push2.sh

# 2. 查看结果
cat push2_api_usage.txt

# 3. 与当前实现对比
grep -o 'self\._song\.[a-zA-Z_]*' ../AbletonMCP_Remote_Script/__init__.py | \
  sed 's/self\._song\.//' | \
  sort -u > current_implementation.txt

# 4. 找出差异
comm -13 current_implementation.txt push2_api_usage.txt
```

### 场景 2: 我想知道 Live 12 新增了什么

```bash
# 1. 运行版本对比工具
python3 compare_versions.py

# 2. 在菜单中选择 "1. 对比两个版本"

# 3. 输入:
#    版本 1: 11.0
#    版本 2: 12.0.2

# 4. 查看新增的类和方法
```

### 场景 3: 我想实时探索 Live API

```bash
# 1. 确保 Ableton Live 正在运行
# 2. 确保 AbletonMCP Remote Script 已加载
# 3. 确保已添加 explore_api 命令（见上面）

# 4. 运行探索器
python3 api_explorer.py

# 5. 按 Enter 浏览不同的 API 类别
```

### 场景 4: 我想实现某个功能，但不知道怎么做

```bash
# 1. 在 Push2 脚本中搜索相关代码
cd "/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/Push2"

# 例如: 我想知道如何设置 track 颜色
grep -r "\.color" . --include="*.py" -B 2 -A 2

# 2. 查看示例代码
# 3. 在自己的 Remote Script 中实现
```

---

## 🎯 输出示例

### extract_api_from_push2.sh 输出
```
=== SONG API ===
tempo
signature_numerator
signature_denominator
tracks
scenes
create_midi_track
create_audio_track
...

=== LISTENERS ===
add_tempo_listener
add_is_playing_listener
add_current_song_time_listener
...
```

### compare_versions.py 输出
```
📊 对比 Live 11.0 vs Live 12.0.2
============================================================

🆕 新增的类 (3):
  • MPESettings
  • TuningSystem
  • ...

🔍 重要类的 API 变化:

  📦 Song:
    🆕 新属性 (2):
      • tuning_system
      • ...
    🆕 新方法 (1):
      • get_build_id()
```

### api_explorer.py 输出
```
🎵 ABLETON LIVE SESSION INFO
============================================================
{
  "tempo": 120.0,
  "track_count": 2,
  ...
}

🔍 探索 SONG API...
============================================================
类别: SONG

📊 属性 (45):
  • tempo: float = 120.0
  • tracks: Vector = Vector[2]
  • scenes: Vector = Vector[8]
  ...

🔧 方法 (25):
  • create_midi_track()
  • create_audio_track()
  • start_playing()
  ...

📈 覆盖率分析:
  • 总可用: 70
  • 已实现: 12
  • 未实现: 58
  • 覆盖率: 17.1%
```

---

## ⚠️ 注意事项

1. **macOS 路径**: 脚本假设 Ableton Live 安装在默认路径，如果不是请修改脚本
2. **Python 版本**: 工具需要 Python 3.6+
3. **网络连接**: `compare_versions.py` 需要从 structure-void.com 下载 XML 文档
4. **Ableton 运行**: `api_explorer.py` 需要 Ableton Live 运行并加载 Remote Script

---

## 🐛 故障排除

### 问题: extract_api_from_push2.sh 找不到 Push2 目录
**解决**: 修改脚本中的 `PUSH2_PATH` 变量

### 问题: api_explorer.py 连接失败
**解决**:
1. 确认 Ableton Live 正在运行
2. 确认 AbletonMCP Remote Script 已在 Preferences 中选择
3. 检查端口 9877 没有被占用

### 问题: compare_versions.py 下载失败
**解决**:
1. 检查网络连接
2. 手动访问 https://structure-void.com/PythonLiveAPI_documentation/ 确认文档存在
3. 如果网站变更，更新脚本中的 URL

---

## 📚 更多资源

- **探索指南**: `../ABLETON_API_EXPLORATION_GUIDE.md`
- **实现路线图**: `../IMPLEMENTATION_ROADMAP.md`
- **分析总结**: `../ANALYSIS_SUMMARY.md`

---

## 🤝 贡献

如果你创建了新的探索工具，欢迎添加到这个目录！

要求：
- 添加工具描述到这个 README
- 包含使用示例
- 添加错误处理
- 提供清晰的输出

---

祝探索愉快！🚀
