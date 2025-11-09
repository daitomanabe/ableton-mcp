#!/bin/bash
# 从 Push2 脚本中提取 API 使用模式
# 这个脚本会分析官方 Push2 Remote Script 来发现可用的 API

PUSH2_PATH="/Applications/Ableton Live 12.app/Contents/App-Resources/MIDI Remote Scripts/Push2"
OUTPUT_FILE="push2_api_usage.txt"

echo "🔍 分析 Push2 Remote Script 的 API 使用..."
echo "路径: $PUSH2_PATH"
echo ""

if [ ! -d "$PUSH2_PATH" ]; then
    echo "❌ 错误: 找不到 Push2 脚本目录"
    echo "请确认 Ableton Live 12 已安装在默认路径"
    exit 1
fi

# 清空输出文件
> "$OUTPUT_FILE"

echo "=== SONG API ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
grep -r "self\.song()\." "$PUSH2_PATH" --include="*.py" 2>/dev/null | \
    sed 's/.*self\.song()\.\([a-zA-Z_][a-zA-Z0-9_]*\).*/\1/' | \
    sort -u >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "=== TRACK API ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
grep -r "\.tracks\[" "$PUSH2_PATH" --include="*.py" -A 1 2>/dev/null | \
    grep -o '\.[a-zA-Z_][a-zA-Z0-9_]*' | \
    sed 's/^\.//' | \
    sort -u >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "=== CLIP API ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
grep -r "\.clip\." "$PUSH2_PATH" --include="*.py" 2>/dev/null | \
    sed 's/.*\.clip\.\([a-zA-Z_][a-zA-Z0-9_]*\).*/\1/' | \
    sort -u >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "=== DEVICE API ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
grep -r "\.devices\[" "$PUSH2_PATH" --include="*.py" -A 1 2>/dev/null | \
    grep -o '\.[a-zA-Z_][a-zA-Z0-9_]*' | \
    sed 's/^\.//' | \
    sort -u >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "=== APPLICATION API ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
grep -r "self\.application()\." "$PUSH2_PATH" --include="*.py" 2>/dev/null | \
    sed 's/.*self\.application()\.\([a-zA-Z_][a-zA-Z0-9_]*\).*/\1/' | \
    sort -u >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "=== LISTENERS (事件监听) ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
grep -r "add_.*_listener" "$PUSH2_PATH" --include="*.py" 2>/dev/null | \
    sed 's/.*\(add_[a-zA-Z_]*_listener\).*/\1/' | \
    sort -u >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "=== COMMON PATTERNS ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 查找常见的方法调用模式
echo "## Scene 相关:" >> "$OUTPUT_FILE"
grep -r "\.scenes" "$PUSH2_PATH" --include="*.py" 2>/dev/null | \
    head -10 >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "## Parameter 控制:" >> "$OUTPUT_FILE"
grep -r "\.parameters" "$PUSH2_PATH" --include="*.py" 2>/dev/null | \
    head -10 >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "## 颜色设置:" >> "$OUTPUT_FILE"
grep -r "\.color" "$PUSH2_PATH" --include="*.py" 2>/dev/null | \
    head -10 >> "$OUTPUT_FILE"

echo "✅ 分析完成！结果保存在: $OUTPUT_FILE"
echo ""
echo "📊 统计信息:"
echo "  Song API 方法数: $(grep -A 1000 "=== SONG API ===" "$OUTPUT_FILE" | grep -B 1000 "=== TRACK API ===" | grep -v "===" | grep -v "^$" | wc -l)"
echo "  Listeners 数量: $(grep -A 1000 "=== LISTENERS ===" "$OUTPUT_FILE" | grep "add_" | wc -l)"

# 显示前 20 行预览
echo ""
echo "📄 前 30 行预览:"
head -30 "$OUTPUT_FILE"

echo ""
echo "💡 使用 'cat $OUTPUT_FILE' 查看完整结果"
