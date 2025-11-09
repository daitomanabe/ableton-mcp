# Ableton MCP 分析总结

## 📚 你的两个核心问题的答案

### ❓ 问题 1: 如何知道当前实现与官方 API 的差距？

**答案**:

#### 当前覆盖率
- **Song API**: ~20% (使用了约 10-12 个方法，总共 60+ 个可用)
- **Track API**: ~30% (使用了约 10 个属性，总共 35+ 个可用)
- **Clip API**: ~10% (仅基础操作，总共 40+ 个可用)
- **Device API**: ~5% (仅只读信息，几乎没有参数控制)
- **Scene API**: 0% (完全未实现)
- **Listeners API**: 0% (完全未实现，这是实时交互的关键)

#### 最大的缺失功能
1. **设备参数控制** - 无法调整效果器/乐器参数
2. **事件监听器** - 无法实时监控 Live 的变化
3. **Scene 操作** - 缺少会话视图的核心功能
4. **高级 Clip 操作** - 无法读取现有音符，只能写入
5. **电平表读取** - 无法获取音频电平

---

### ❓ 问题 2: 如何发现 Live 12 新增的功能？

**方法汇总**:

#### 方法 1: 查看官方反编译脚本 (最可靠)
```bash
# 克隆 Live 12 的反编译脚本
git clone https://github.com/gluon/AbletonLive12_MIDIRemoteScripts.git

# 查看更新历史
cd AbletonLive12_MIDIRemoteScripts
git log --since="2024-01-01" --oneline

# 对比 Live 11 和 Live 12
# 下载 Live 11 版本对比
```

#### 方法 2: 使用 API 文档对比 (在线)
- **Live 12.0.2 XML**: https://structure-void.com/PythonLiveAPI_documentation/Live12.0.2.xml
- **Live 11.0 XML**: https://structure-void.com/PythonLiveAPI_documentation/Live11.0.xml
- **运行对比工具**: `python3 tools/compare_versions.py`

#### 方法 3: 直接探索本地安装 (实时)
```bash
# 分析官方 Push2 脚本使用的 API
cd "/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/Push2"

# 提取 Song API 用法
grep -r "self.song()\." . --include="*.py" | \
  sed 's/.*self\.song()\.\([a-zA-Z_]*\).*/\1/' | \
  sort -u

# 或者运行我们的提取脚本
./tools/extract_api_from_push2.sh
```

#### 方法 4: 使用探索工具 (动态发现)
在 Remote Script 中添加探索代码，运行时检查所有可用属性：

```python
# 在 AbletonMCP_Remote_Script/__init__.py 中
def explore_api(self):
    for attr in dir(self.song()):
        if not attr.startswith('_'):
            self.log_message(f"{attr}: {type(getattr(self.song(), attr))}")
```

查看日志：
```bash
tail -f ~/Library/Preferences/Ableton/Live\ 12.*/Log.txt
```

---

## 🎯 Live 12 的主要新增功能

根据社区文档和反编译脚本，Live 12 新增：

### Application 级别
```python
app.get_build_id()        # 新增 - 构建 ID
app.get_variant()         # 新增 - 版本变体 (Intro/Standard/Suite)
app.show_message(msg)     # 增强 - 更好的消息显示
```

### Song 级别
- 改进的 MIDI 映射 API
- 更好的浏览器集成
- Comping 支持（音频编辑功能）

### Track 级别
- 改进的输入/输出路由选项
- 更好的冻结功能 API

### Clip 级别
- `get_notes_extended()` / `set_notes_extended()` - 支持音符表情（Expression）
- MPE (MIDI Polyphonic Expression) 支持

---

## 📁 我为你创建的资源

### 1. 完整分析指南
**文件**: `ABLETON_API_EXPLORATION_GUIDE.md`
**内容**:
- 如何发现完整的 API
- 当前实现的详细覆盖分析
- 所有未实现但可用的功能（分类列出）
- 实用探索工具和脚本
- 版本升级检测策略

### 2. 实现路线图
**文件**: `IMPLEMENTATION_ROADMAP.md`
**内容**:
- 8 个开发阶段的详细计划
- 每个功能的优先级和难度评估
- 完整的功能列表和代码示例
- 版本发布时间表

### 3. 实用工具脚本

#### `tools/api_explorer.py`
**功能**: 实时探索 Ableton Live API
```bash
python3 tools/api_explorer.py
```
这会连接到你的 Ableton Live，探索所有可用的 API 并显示：
- Song, Track, Clip, Device 等所有属性
- 可用的方法
- 当前实现的覆盖率

**注意**: 需要先在 Remote Script 中实现 `explore_api` 命令（参考探索指南）

#### `tools/extract_api_from_push2.sh`
**功能**: 从官方 Push2 脚本提取 API 使用模式
```bash
chmod +x tools/extract_api_from_push2.sh
./tools/extract_api_from_push2.sh
```
这会生成 `push2_api_usage.txt`，列出 Push2 使用的所有 API。

#### `tools/compare_versions.py`
**功能**: 对比不同版本的 API 变化
```bash
# 需要安装 requests
pip install requests

python3 tools/compare_versions.py
```
这会下载 Live 10/11/12 的 API 文档并对比差异。

---

## 🚀 快速开始：发现未实现的功能

### Step 1: 运行 Push2 API 提取器
```bash
cd /home/user/ableton-mcp
chmod +x tools/extract_api_from_push2.sh
./tools/extract_api_from_push2.sh
```

查看结果：
```bash
cat push2_api_usage.txt
```

### Step 2: 对比 Live 版本
```bash
python3 tools/compare_versions.py
# 选择 "1" 对比版本
# 输入: 11.0 和 12.0.2
```

### Step 3: 查看当前实现
```bash
# 查看当前使用的 Song API
grep -o 'self\._song\.[a-zA-Z_]*' AbletonMCP_Remote_Script/__init__.py | \
  sed 's/self\._song\.//' | \
  sort -u
```

### Step 4: 找到差距
对比 Step 1 和 Step 3 的结果，差距就是未实现的功能。

---

## 📊 关键发现

### 最有价值但未实现的 API

#### 1. Device.parameters (设备参数) ⭐⭐⭐
```python
device = track.devices[0]
for param in device.parameters:
    print(f"{param.name}: {param.value}")
    param.value = 0.5  # 调整参数
```
**价值**: 允许 Claude 调整任何效果器/乐器的参数
**实现难度**: 低
**预计代码**: ~50 行

#### 2. Listeners (事件监听) ⭐⭐⭐
```python
def on_tempo_change():
    print(f"Tempo changed to {song.tempo}")

song.add_tempo_listener(on_tempo_change)
```
**价值**: 实时反馈，Claude 可以感知 Live 的变化
**实现难度**: 中-高（需要重新设计通信架构）
**预计代码**: ~200 行

#### 3. Scene API ⭐⭐⭐
```python
scene = song.scenes[0]
scene.fire()  # 触发场景
scene.name = "Intro"
```
**价值**: 完整的会话视图控制
**实现难度**: 低
**预计代码**: ~100 行

#### 4. Clip.get_notes() ⭐⭐⭐
```python
notes = clip.get_notes(0, 0, 4, 128)  # 读取现有音符
```
**价值**: 可以分析和修改现有 MIDI
**实现难度**: 低-中
**预计代码**: ~30 行

#### 5. Track.output_meter_* (电平表) ⭐⭐
```python
level = track.output_meter_left
```
**价值**: 可视化反馈，混音辅助
**实现难度**: 中（需要定时采样）
**预计代码**: ~50 行

---

## 🎓 学习资源

### 官方资源（间接）
1. **Live Object Model**: https://docs.cycling74.com/max8/vignettes/live_object_model
   - 官方文档，虽然是为 Max for Live，但 API 相同

2. **Ableton Forum**: https://forum.ableton.com/
   - 搜索 "Remote Script" 或 "Python API"

### 社区资源
1. **Structure Void (Julien Bayle)**: https://structure-void.com/
   - 最权威的非官方资源
   - 提供各版本的 API XML 文档

2. **GitHub Repositories**:
   - https://github.com/gluon/AbletonLive12_MIDIRemoteScripts
   - https://github.com/gluon/AbletonLive11_MIDIRemoteScripts

3. **NSUSpray API Doc**: https://nsuspray.github.io/Live_API_Doc/
   - 更友好的 API 浏览界面

### 本地学习资源
1. **官方 Remote Scripts**:
   ```
   /Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/
   ```
   - Push2/ - 最完整的参考
   - APC/ - MIDI 控制器示例
   - _Framework/ - 框架基础类

2. **Log 文件**:
   ```
   ~/Library/Preferences/Ableton/Live 12.*/Log.txt
   ```
   - 查看 Remote Script 的输出

---

## 💡 实用技巧

### 1. 快速查找特定功能
```bash
# 查找如何设置 track 颜色
grep -r "\.color" "/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/Push2" \
  --include="*.py" -B 2 -A 2
```

### 2. 了解参数类型
```python
# 在 Remote Script 中打印类型信息
attr = getattr(obj, 'some_attribute')
self.log_message(f"Type: {type(attr)}, Value: {attr}")
```

### 3. 安全实验
- 在测试项目中实验，不要在重要项目中
- 经常保存
- 使用 `try-except` 包装所有 API 调用

### 4. 性能优化
- 批量操作减少通信往返
- 缓存不变的数据（如设备名称）
- 使用 listeners 而不是轮询

---

## 🔍 常见问题

### Q: 为什么 Ableton 不提供官方文档？
A: Ableton 将 Remote Script API 视为内部 API，不保证向后兼容。官方只支持 Max for Live 的 LOM API。

### Q: Remote Script 可以做录音吗？
A: API 本身支持触发录音（`song.session_record`），但不能直接访问音频数据。

### Q: 可以控制第三方插件吗？
A: 可以通过 `device.parameters` 控制任何插件的参数，但无法访问插件的自定义 UI。

### Q: 如何调试 Remote Script？
A: 使用 `self.log_message()` 输出到 Log.txt，或使用 `self.show_message()` 在 Live 界面显示。

### Q: Python 2 还是 Python 3？
A: Live 11+ 使用 Python 3.x，Live 10 使用 Python 2.7。当前代码兼容两者。

---

## 📝 下一步建议

### 立即可做
1. ✅ 阅读 `ABLETON_API_EXPLORATION_GUIDE.md`
2. ✅ 运行 `tools/extract_api_from_push2.sh`
3. ✅ 查看 `IMPLEMENTATION_ROADMAP.md` 选择要实现的功能

### 短期目标（1-2 周）
1. 实现设备参数控制（最高价值）
2. 添加 Scene 操作
3. 实现 Track 颜色管理

### 中期目标（1-2 月）
1. 实现事件监听系统（需要架构升级）
2. 添加高级 Clip 操作
3. 完善 Browser 功能

### 长期愿景（3-6 月）
1. 达到 60%+ 的 API 覆盖率
2. 发布 v2.0 主要版本
3. 建立社区贡献流程

---

## 🤝 贡献

如果你实现了新功能，欢迎：
1. Fork 这个仓库
2. 创建 feature 分支
3. 提交 Pull Request
4. 包含测试和文档

---

## 📞 获取帮助

- **Ableton Forum**: 搜索或提问关于 Remote Script 的问题
- **GitHub Issues**: 报告 bug 或提出功能请求
- **Discord**: 原作者的社区 - https://discord.gg/3ZrMyGKnaU

---

## 总结

你现在有了：
1. ✅ **完整的 API 分析** - 知道有什么可用
2. ✅ **当前实现的覆盖率** - 知道已实现什么
3. ✅ **差距清单** - 知道缺少什么
4. ✅ **发现新功能的方法** - 知道如何跟踪更新
5. ✅ **实用工具** - 自动化探索过程
6. ✅ **实现路线图** - 知道下一步做什么

**最重要的发现**：当前实现只覆盖了 Ableton Live API 的约 **15-20%**，最有价值的缺失功能是：
1. 设备参数控制
2. 事件监听
3. Scene 操作

开始探索吧！🚀
