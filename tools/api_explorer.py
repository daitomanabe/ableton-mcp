#!/usr/bin/env python3
"""
Ableton Live API Explorer
用于探索和对比 API 的实用工具

使用方法:
1. 在 AbletonMCP_Remote_Script/__init__.py 中添加 explore_api 命令
2. 运行此脚本: python3 api_explorer.py
"""

import socket
import json
import sys
from typing import Dict, Any, List

DEFAULT_PORT = 9877
HOST = "localhost"

class AbletonExplorer:
    def __init__(self, host: str = HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self) -> bool:
        """连接到 Ableton Remote Script"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"✅ 已连接到 Ableton Live ({self.host}:{self.port})")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("确保 Ableton Live 正在运行且 AbletonMCP Remote Script 已加载")
            return False

    def disconnect(self):
        """断开连接"""
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送命令并返回响应"""
        if not self.sock and not self.connect():
            raise ConnectionError("未连接到 Ableton")

        command = {
            "type": command_type,
            "params": params or {}
        }

        try:
            # 发送命令
            self.sock.sendall(json.dumps(command).encode('utf-8'))

            # 接收响应
            chunks = []
            while True:
                chunk = self.sock.recv(8192)
                if not chunk:
                    break
                chunks.append(chunk)

                # 尝试解析 JSON
                try:
                    data = b''.join(chunks)
                    response = json.loads(data.decode('utf-8'))
                    return response.get("result", {})
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            print(f"❌ 命令执行错误: {e}")
            return {}

    def explore_category(self, category: str) -> Dict[str, Any]:
        """探索特定类别的 API"""
        print(f"\n🔍 探索 {category.upper()} API...")
        result = self.send_command("explore_api", {"category": category})
        return result

    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        return self.send_command("get_session_info")

    def print_api_info(self, result: Dict[str, Any]):
        """打印 API 信息"""
        if "error" in result:
            print(f"⚠️  {result['error']}")
            return

        print(f"\n{'='*60}")
        print(f"类别: {result.get('category', 'unknown').upper()}")
        print(f"{'='*60}")

        # 打印属性
        properties = result.get('properties', [])
        if properties:
            print(f"\n📊 属性 ({len(properties)}):")
            for prop in sorted(properties, key=lambda x: x['name']):
                value_str = f" = {prop.get('value', '')}" if 'value' in prop else ""
                print(f"  • {prop['name']}: {prop['type']}{value_str}")

        # 打印方法
        methods = result.get('methods', [])
        if methods:
            print(f"\n🔧 方法 ({len(methods)}):")
            for method in sorted(methods, key=lambda x: x['name']):
                print(f"  • {method['name']}()")

        # 打印错误的属性
        attributes = result.get('attributes', [])
        if attributes:
            print(f"\n⚠️  无法访问的属性 ({len(attributes)}):")
            for attr in attributes:
                print(f"  • {attr['name']}: {attr.get('error', 'unknown error')}")

    def compare_with_implemented(self, category: str, implemented: List[str]):
        """对比已实现的功能"""
        result = self.explore_category(category)

        if "error" in result:
            print(f"⚠️  {result['error']}")
            return

        all_available = set()
        for prop in result.get('properties', []):
            all_available.add(prop['name'])
        for method in result.get('methods', []):
            all_available.add(method['name'])

        implemented_set = set(implemented)
        not_implemented = all_available - implemented_set

        print(f"\n📈 覆盖率分析:")
        print(f"  • 总可用: {len(all_available)}")
        print(f"  • 已实现: {len(implemented_set)}")
        print(f"  • 未实现: {len(not_implemented)}")
        print(f"  • 覆盖率: {len(implemented_set)/len(all_available)*100:.1f}%")

        if not_implemented:
            print(f"\n💡 未实现的功能 (前 20 个):")
            for name in sorted(list(not_implemented))[:20]:
                print(f"  • {name}")


def main():
    explorer = AbletonExplorer()

    if not explorer.connect():
        sys.exit(1)

    try:
        # 获取会话信息
        print("\n" + "="*60)
        print("🎵 ABLETON LIVE SESSION INFO")
        print("="*60)
        session = explorer.get_session_info()
        print(json.dumps(session, indent=2))

        # 探索不同类别
        categories = ["song", "track", "clip", "device", "application", "browser"]

        print("\n" + "="*60)
        print("🔍 API 探索")
        print("="*60)

        for category in categories:
            result = explorer.explore_category(category)
            explorer.print_api_info(result)
            input(f"\n按 Enter 继续探索下一个类别...")

        # 覆盖率分析
        print("\n" + "="*60)
        print("📊 当前实现覆盖率分析")
        print("="*60)

        # Song API 已实现的功能
        song_implemented = [
            'tempo', 'signature_numerator', 'signature_denominator',
            'tracks', 'return_tracks', 'master_track', 'create_midi_track',
            'is_playing', 'start_playing', 'stop_playing', 'view'
        ]

        explorer.compare_with_implemented("song", song_implemented)

        # Track API 已实现的功能
        track_implemented = [
            'name', 'mute', 'solo', 'arm', 'clip_slots', 'devices',
            'mixer_device', 'has_audio_input', 'has_midi_input'
        ]

        explorer.compare_with_implemented("track", track_implemented)

    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        explorer.disconnect()
        print("\n✅ 已断开连接")


if __name__ == "__main__":
    main()
