# Ableton Live 12 API 完全探索指南

## 目录
1. [如何发现 Ableton Live 12 的完整 API](#1-如何发现-ableton-live-12-的完整-api)
2. [当前实现的功能覆盖分析](#2-当前实现的功能覆盖分析)
3. [未实现但可用的功能](#3-未实现但可用的功能)
4. [实用探索工具和脚本](#4-实用探索工具和脚本)

---

## 1. 如何发现 Ableton Live 12 的完整 API

### 1.1 官方资源（间接）

**重要事实：Ableton 不提供官方的 Python Remote Script API 文档！**

但你可以通过以下途径获取：

#### A. Live Object Model (LOM) 文档
- **官方文档**: https://docs.cycling74.com/max8/vignettes/live_object_model
- **说明**: 这是为 Max for Live 提供的，但 Python API 和 Max API 共享相同的对象模型
- **适用版本**: Live 12.1

#### B. 本地反编译源码
```bash
# macOS 路径
cd "/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts"

# 你会看到所有官方 Remote Scripts:
ls -la
# _Framework/        - 框架基础类
# Push/             - Push 控制器脚本
# Push2/            - Push 2 控制器脚本
# APC/              - APC 系列
# 等等...
```

**关键**: 这些是 `.pyc` 字节码文件，但在 Python 3 中你可以直接阅读 `.py` 文件（如果存在）。

#### C. 社区维护的反编译版本
- **Live 12**: https://github.com/gluon/AbletonLive12_MIDIRemoteScripts
- **Live 11**: https://github.com/gluon/AbletonLive11_MIDIRemoteScripts
- **作者**: Julien Bayle (community leader)

#### D. 非官方 API 文档
- **Live 12.0.2 XML**: https://structure-void.com/PythonLiveAPI_documentation/Live12.0.2.xml
- **Live 11.0 XML**: https://structure-void.com/PythonLiveAPI_documentation/Live11.0.xml
- **更友好的版本**: https://nsuspray.github.io/Live_API_Doc/

---

### 1.2 本地探索方法

#### 方法 1: 使用 Python 内省检查 Live API

创建一个诊断脚本在你的 Remote Script 中：

```python
# 在 AbletonMCP_Remote_Script/__init__.py 中添加
def explore_api(self):
    """探索当前 Live API 的所有可用功能"""
    song = self.song()

    # 列出 Song 对象的所有属性和方法
    song_attrs = [attr for attr in dir(song) if not attr.startswith('_')]

    # 输出到 Log.txt
    self.log_message("=== SONG API ===")
    for attr in sorted(song_attrs):
        try:
            val = getattr(song, attr)
            self.log_message(f"{attr}: {type(val).__name__}")
        except:
            self.log_message(f"{attr}: [ERROR accessing]")

    # 探索 Track
    if len(song.tracks) > 0:
        track = song.tracks[0]
        track_attrs = [attr for attr in dir(track) if not attr.startswith('_')]

        self.log_message("\n=== TRACK API ===")
        for attr in sorted(track_attrs):
            try:
                val = getattr(track, attr)
                self.log_message(f"{attr}: {type(val).__name__}")
            except:
                self.log_message(f"{attr}: [ERROR accessing]")

    # 探索 Application
    app = self.application()
    app_attrs = [attr for attr in dir(app) if not attr.startswith('_')]

    self.log_message("\n=== APPLICATION API ===")
    for attr in sorted(app_attrs):
        try:
            val = getattr(app, attr)
            self.log_message(f"{attr}: {type(val).__name__}")
        except:
            self.log_message(f"{attr}: [ERROR accessing]")

# 在 __init__ 中调用
def __init__(self, c_instance):
    ControlSurface.__init__(self, c_instance)
    # ... 其他初始化代码
    self.explore_api()  # 运行一次探索
```

**查看输出**:
```bash
# macOS
tail -f ~/Library/Preferences/Ableton/Live\ 12.*/Log.txt
```

#### 方法 2: 研究官方 Remote Scripts

最好的学习资源是 **Push2** 脚本，它使用了几乎所有的 API：

```bash
cd "/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/Push2"
grep -r "self\._song\." . --include="*.py" | head -20
```

---

## 2. 当前实现的功能覆盖分析

### 2.1 已实现的核心 API

| Live API 类别 | 当前实现 | 使用的方法 |
|--------------|----------|-----------|
| **Song (会话)** | ✅ 部分 | `tempo`, `signature_numerator`, `signature_denominator`, `tracks`, `return_tracks`, `master_track` |
| **Track (轨道)** | ✅ 部分 | `name`, `mute`, `solo`, `arm`, `clip_slots`, `devices`, `mixer_device`, `has_audio_input`, `has_midi_input` |
| **Clip (片段)** | ✅ 基础 | `name`, `length`, `is_playing`, `is_recording`, `set_notes()` |
| **ClipSlot (片段槽)** | ✅ 基础 | `has_clip`, `create_clip()`, `fire()`, `stop()` |
| **Device (设备)** | ✅ 只读 | `name`, `class_name`, `can_have_drum_pads`, `can_have_chains` |
| **Browser (浏览器)** | ✅ 部分 | `instruments`, `sounds`, `drums`, `audio_effects`, `midi_effects`, `load_item()` |
| **MixerDevice (混音器)** | ✅ 只读 | `volume.value`, `panning.value` |
| **Application (应用)** | ✅ 基础 | `browser` |

### 2.2 API 使用统计

```python
# 当前使用的 Song 方法（已实现）:
self._song.tempo                      # 读写
self._song.signature_numerator        # 只读
self._song.signature_denominator      # 只读
self._song.tracks                     # 只读列表
self._song.return_tracks              # 只读列表
self._song.master_track               # 只读
self._song.create_midi_track(index)   # 写入
self._song.is_playing                 # 只读
self._song.start_playing()            # 写入
self._song.stop_playing()             # 写入
self._song.view.selected_track        # 读写

# 估计覆盖率: 约 15-20% 的 Song API
```

---

## 3. 未实现但可用的功能

### 3.1 Song 级别（高优先级）

#### 自动化和包络
```python
# 未实现但非常有用:
self._song.create_audio_track(index)           # 创建音频轨道
self._song.delete_track(index)                 # 删除轨道
self._song.duplicate_track(index)              # 复制轨道
self._song.create_scene(index)                 # 创建场景
self._song.delete_scene(index)                 # 删除场景
self._song.scenes                              # 场景列表
self._song.view.selected_scene                 # 当前选中的场景
self._song.view.selected_track                 # 已实现但可增强
self._song.visible_tracks                      # 可见轨道
self._song.arrangement_overdub                 # 录音覆盖
self._song.back_to_arranger                    # 返回编曲视图
self._song.session_record                      # 会话录音
self._song.metronome                           # 节拍器
self._song.punch_in                            # 打入录音
self._song.punch_out                           # 打出录音
self._song.record_mode                         # 录音模式
self._song.re_enable_automation_enabled        # 自动化
self._song.session_automation_record           # 会话自动化录音
self._song.loop                                # 循环开关
self._song.loop_start                          # 循环起点
self._song.loop_length                         # 循环长度
self._song.current_song_time                   # 当前播放位置
self._song.jump_by(amount)                     # 跳转播放位置
self._song.jump_to_next_cue()                  # 跳到下一个标记
self._song.jump_to_prev_cue()                  # 跳到上一个标记
self._song.cue_points                          # 标记点列表
self._song.nudge_down()                        # 微调
self._song.nudge_up()                          # 微调
self._song.undo()                              # 撤销
self._song.redo()                              # 重做
self._song.get_beats_loop_start()              # 获取节拍循环起点
self._song.get_current_beats_song_time()       # 获取当前节拍时间
```

#### Listeners (事件监听)
```python
# 强大但未实现的功能:
self._song.add_tempo_listener(callback)                # 监听速度变化
self._song.add_is_playing_listener(callback)           # 监听播放状态
self._song.add_current_song_time_listener(callback)    # 监听播放位置
self._song.add_tracks_listener(callback)               # 监听轨道变化
self._song.add_scenes_listener(callback)               # 监听场景变化

# 示例用法:
def on_tempo_change():
    self.log_message(f"Tempo changed to: {self._song.tempo}")

self._song.add_tempo_listener(on_tempo_change)
```

### 3.2 Track 级别（高优先级）

```python
track = self._song.tracks[0]

# 未实现:
track.color                                    # 轨道颜色
track.color_index                              # 颜色索引
track.is_foldable                              # 是否可折叠（Group Track）
track.is_grouped                               # 是否在 Group 中
track.group_track                              # 所属的 Group Track
track.available_input_routing_channels         # 可用输入路由
track.available_input_routing_types            # 可用输入类型
track.available_output_routing_channels        # 可用输出路由
track.available_output_routing_types           # 可用输出类型
track.current_input_routing                    # 当前输入路由
track.current_input_sub_routing                # 当前输入子路由
track.current_monitoring_state                 # 监听状态 (In/Auto/Off)
track.current_output_routing                   # 当前输出路由
track.current_output_sub_routing               # 当前输出子路由
track.input_meter_level                        # 输入电平
track.output_meter_level                       # 输出电平（重要！）
track.input_meter_left                         # 左声道输入电平
track.input_meter_right                        # 右声道输入电平
track.output_meter_left                        # 左声道输出电平
track.output_meter_right                       # 右声道输出电平
track.playing_slot_index                       # 正在播放的 clip 索引
track.fired_slot_index                         # 已触发的 clip 索引
track.is_showing_chains                        # 是否显示链
track.can_show_chains                          # 是否可以显示链

# 自动化相关:
track.view.select_instrument()                 # 选择乐器
track.view.is_collapsed                        # 是否折叠
track.view.device_insert_mode                  # 设备插入模式

# 设备控制:
track.delete_device(index)                     # 删除设备
track.duplicate_clip_slot(index)               # 复制片段槽

# Listeners:
track.add_name_listener(callback)              # 监听名称变化
track.add_color_listener(callback)             # 监听颜色变化
track.add_devices_listener(callback)           # 监听设备变化
track.add_mute_listener(callback)              # 监听静音变化
track.add_solo_listener(callback)              # 监听独奏变化
track.add_arm_listener(callback)               # 监听录音准备状态
track.add_output_meter_left_listener(callback) # 监听电平表（重要！）
```

### 3.3 Clip 级别（中优先级）

```python
clip = track.clip_slots[0].clip

# 未实现:
clip.color                                     # clip 颜色
clip.color_index                               # 颜色索引
clip.start_marker                              # 起始标记
clip.end_marker                                # 结束标记
clip.loop_start                                # 循环起点
clip.loop_end                                  # 循环终点
clip.looping                                   # 是否循环
clip.warping                                   # 是否启用 warp
clip.warp_mode                                 # Warp 模式
clip.pitch_coarse                              # 粗调音高
clip.pitch_fine                                # 细调音高
clip.gain                                      # 增益
clip.signature_numerator                       # 拍号分子
clip.signature_denominator                     # 拍号分母
clip.launch_mode                               # 启动模式
clip.launch_quantization                       # 启动量化

# MIDI Clip 特有:
clip.get_notes(from_time, from_pitch, time_span, pitch_span)  # 获取音符（比 set_notes 更强）
clip.get_selected_notes()                      # 获取选中的音符
clip.select_all_notes()                        # 全选音符
clip.deselect_all_notes()                      # 取消全选
clip.replace_selected_notes(notes)             # 替换选中的音符
clip.get_notes_extended(...)                   # 扩展音符获取
clip.set_notes_extended(...)                   # 扩展音符设置（支持表情）

# Audio Clip 特有:
clip.sample_length                             # 采样长度
clip.file_path                                 # 文件路径

# Listeners:
clip.add_playing_status_listener(callback)     # 监听播放状态
clip.add_name_listener(callback)               # 监听名称变化
clip.add_color_listener(callback)              # 监听颜色变化
clip.add_notes_listener(callback)              # 监听音符变化（重要！）
```

### 3.4 Device 级别（高优先级）

```python
device = track.devices[0]

# 未实现:
device.parameters                              # 参数列表（关键！）
device.is_active                               # 是否激活
device.view.is_collapsed                       # 是否折叠

# 参数控制（非常重要！）:
for param in device.parameters:
    param.name                                 # 参数名称
    param.value                                # 参数值
    param.min                                  # 最小值
    param.max                                  # 最大值
    param.default_value                        # 默认值
    param.is_enabled                           # 是否启用
    param.is_quantized                         # 是否量化
    param.value_items                          # 值选项（用于枚举参数）
    param.add_value_listener(callback)         # 监听值变化

# Drum Rack 特有:
device.drum_pads                               # 鼓垫列表
device.view.selected_drum_pad                  # 选中的鼓垫

# Rack 特有:
device.chains                                  # 链列表
device.view.selected_chain                     # 选中的链
```

### 3.5 Browser 级别（需增强）

```python
browser = self.application().browser

# 当前已实现但可增强:
browser.instruments                            # ✅ 已实现
browser.sounds                                 # ✅ 已实现
browser.drums                                  # ✅ 已实现
browser.audio_effects                          # ✅ 已实现
browser.midi_effects                           # ✅ 已实现
browser.load_item(item)                        # ✅ 已实现

# 未实现:
browser.clips                                  # Clip 浏览器
browser.samples                                # 采样浏览器
browser.plugins                                # 插件浏览器
browser.user_library                           # 用户库
browser.packs                                  # Pack 列表
browser.filter_type                            # 筛选类型
browser.hotswap_target                         # Hotswap 目标

# 浏览器项目:
item.is_selected                               # 是否选中
item.source                                    # 来源
```

### 3.6 Scene 级别（未实现）

```python
scene = self._song.scenes[0]

# 完全未实现:
scene.name                                     # 场景名称
scene.color                                    # 颜色
scene.color_index                              # 颜色索引
scene.clip_slots                               # 片段槽列表
scene.fire()                                   # 触发场景
scene.fire_as_selected()                       # 作为选中触发
scene.add_name_listener(callback)              # 监听名称变化
```

### 3.7 Application 级别

```python
app = self.application()

# 已实现:
app.browser                                    # ✅ 已实现

# 未实现:
app.get_major_version()                        # 主版本号
app.get_minor_version()                        # 次版本号
app.get_bugfix_version()                       # 修复版本号
app.get_document()                             # 获取当前文档（Song）
app.open_dialog()                              # 打开对话框
app.view.show_view(view_name)                  # 显示特定视图
app.view.hide_view(view_name)                  # 隐藏特定视图
app.view.is_view_visible(view_name)            # 视图是否可见

# Live 12 新增（重要！）:
app.get_build_id()                             # 构建 ID
app.get_variant()                              # 变体（Intro/Standard/Suite）
app.show_message(message)                      # 显示消息（已部分使用）
```

---

## 4. 实用探索工具和脚本

### 4.1 API 探索器脚本

创建一个独立的命令来探索 API：

```python
# 在 _process_command 中添加:
elif command_type == "explore_api":
    category = params.get("category", "song")
    response["result"] = self._explore_api_category(category)

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

### 4.2 使用探索器

在 MCP Server 中添加工具：

```python
@mcp.tool()
def explore_live_api(ctx: Context, category: str = "song") -> str:
    """
    探索 Ableton Live API 的特定类别

    Parameters:
    - category: 类别名称 (song, track, clip, device, application, browser)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("explore_api", {"category": category})

        # 格式化输出
        output = f"=== {category.upper()} API ===\n\n"

        if "error" in result:
            return f"Error: {result['error']}"

        output += f"## Properties ({len(result.get('properties', []))}):\n"
        for prop in result.get('properties', []):
            output += f"  • {prop['name']}: {prop['type']}"
            if 'value' in prop:
                output += f" = {prop['value']}"
            output += "\n"

        output += f"\n## Methods ({len(result.get('methods', []))}):\n"
        for method in result.get('methods', []):
            output += f"  • {method['name']}()\n"

        return output
    except Exception as e:
        return f"Error exploring API: {str(e)}"
```

### 4.3 对比脚本

创建一个脚本来对比当前实现和可用 API：

```bash
#!/bin/bash
# compare_api.sh

echo "=== Comparing Implemented vs Available API ==="

# 提取当前实现使用的方法
echo "## Currently Implemented:"
grep -r "self\._song\." AbletonMCP_Remote_Script/__init__.py | \
  sed 's/.*self\._song\.\([a-zA-Z_]*\).*/\1/' | \
  sort -u

echo ""
echo "## Available in Push2 Script:"
grep -r "self\.song()\." "/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/Push2" \
  --include="*.py" | \
  sed 's/.*self\.song()\.\([a-zA-Z_]*\).*/\1/' | \
  sort -u | \
  head -50
```

---

## 5. 推荐的功能扩展优先级

基于实用性和需求，建议按以下顺序添加功能：

### 优先级 1（高价值，易实现）
1. **设备参数控制** - `device.parameters`
   - 允许调整任何设备的参数
   - 实现难度：低

2. **Track 颜色** - `track.color`, `track.color_index`
   - 视觉组织
   - 实现难度：低

3. **Scene 操作** - `scene.fire()`, `scene.name`
   - 场景触发和管理
   - 实现难度：低

4. **Clip 高级操作** - `clip.get_notes()`, `clip.color`
   - 更强大的 MIDI 编辑
   - 实现难度：中

5. **循环和播放位置** - `song.loop_start`, `song.current_song_time`
   - 播放控制
   - 实现难度：低

### 优先级 2（高价值，中等实现）
1. **电平表** - `track.output_meter_left`, `track.output_meter_right`
   - 可视化反馈
   - 实现难度：中（需要定时采样）

2. **自动化录音** - `song.session_automation_record`
   - 创作工具
   - 实现难度：中

3. **事件监听器** - 各种 `add_*_listener`
   - 实时反馈
   - 实现难度：中（需要管理回调）

4. **音频轨道** - `create_audio_track`
   - 完整性
   - 实现难度：低

5. **轨道删除/复制** - `delete_track`, `duplicate_track`
   - 工作流增强
   - 实现难度：低

### 优先级 3（专业功能）
1. **Warp 控制** - `clip.warping`, `clip.warp_mode`
   - 音频处理
   - 实现难度：中

2. **路由控制** - `track.current_input_routing`
   - 高级配置
   - 实现难度：高

3. **Drum Rack 控制** - `device.drum_pads`
   - 鼓机编程
   - 实现难度：高

---

## 6. 版本升级检测策略

### 6.1 自动检测脚本

```python
def check_api_changes(self):
    """检测 API 变化"""
    app = self.application()

    # 获取版本信息
    version_info = {
        "major": app.get_major_version() if hasattr(app, 'get_major_version') else None,
        "minor": app.get_minor_version() if hasattr(app, 'get_minor_version') else None,
        "bugfix": app.get_bugfix_version() if hasattr(app, 'get_bugfix_version') else None,
    }

    # Live 12 特有的新方法
    new_in_12 = []
    if hasattr(app, 'get_build_id'):
        new_in_12.append('get_build_id')
    if hasattr(app, 'get_variant'):
        new_in_12.append('get_variant')

    return {
        "version": version_info,
        "new_methods": new_in_12
    }
```

### 6.2 对比 GitHub 更新

定期检查：
```bash
# 克隆最新的反编译脚本
git clone https://github.com/gluon/AbletonLive12_MIDIRemoteScripts.git

# 对比变化
cd AbletonLive12_MIDIRemoteScripts
git log --since="2024-01-01" --oneline
```

---

## 7. 快速参考

### 完整的 Live Object Model 结构

```
Application
  └─ browser
      ├─ instruments
      ├─ sounds
      ├─ drums
      ├─ audio_effects
      ├─ midi_effects
      ├─ clips
      ├─ samples
      └─ plugins

Song
  ├─ tracks[] (Track)
  │   ├─ clip_slots[] (ClipSlot)
  │   │   └─ clip (Clip)
  │   ├─ devices[] (Device)
  │   │   └─ parameters[] (DeviceParameter)
  │   └─ mixer_device (MixerDevice)
  ├─ return_tracks[] (Track)
  ├─ master_track (Track)
  ├─ scenes[] (Scene)
  ├─ cue_points[] (CuePoint)
  └─ view
      ├─ selected_track
      ├─ selected_scene
      └─ highlighted_clip_slot
```

### 官方资源汇总

| 资源 | URL | 说明 |
|------|-----|------|
| Live Object Model | https://docs.cycling74.com/max8/vignettes/live_object_model | 官方 LOM 文档 |
| Live 12 Scripts | https://github.com/gluon/AbletonLive12_MIDIRemoteScripts | 反编译源码 |
| API XML 文档 | https://structure-void.com/PythonLiveAPI_documentation/ | 各版本 API |
| 友好的 API 文档 | https://nsuspray.github.io/Live_API_Doc/ | 易读版本 |
| Push2 脚本 | 本地安装 | 最佳学习资源 |

---

## 总结

**回答你的两个问题：**

### 1. 如何知道当前实现的覆盖程度？
- 当前实现约覆盖 **15-20%** 的 Song API
- 约 **30%** 的 Track API
- 约 **10%** 的 Clip API
- **0%** 的 Device 参数控制（这是最大的缺失！）
- **0%** 的 Scene API
- **0%** 的 Listener API（事件监听）

### 2. 如何发现新版本的新功能？
1. **对比 GitHub**: 定期检查 gluon 的仓库更新
2. **运行探索脚本**: 使用上面的 `explore_api` 工具
3. **研究官方脚本**: 查看 Push2 等官方脚本的新用法
4. **监控社区**: Ableton Forum, structure-void.com
5. **使用 hasattr 检测**: 在代码中检测新方法的存在

**最重要的未实现功能：**
- 🔴 Device 参数控制
- 🔴 Event Listeners
- 🔴 Scene 控制
- 🟡 电平表读取
- 🟡 高级 Clip 操作（get_notes, 颜色等）
