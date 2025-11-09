#!/usr/bin/env python3
"""
版本对比工具
对比不同版本的 Ableton Live API 变化

使用方法:
python3 compare_versions.py
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Set, List
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class APIClass:
    name: str
    properties: Set[str]
    methods: Set[str]

    def __hash__(self):
        return hash(self.name)

class VersionComparator:
    def __init__(self):
        self.versions = {
            "10.0.2": "https://structure-void.com/PythonLiveAPI_documentation/Live10.0.2.xml",
            "10.1": "https://structure-void.com/PythonLiveAPI_documentation/Live10.1.xml",
            "11.0": "https://structure-void.com/PythonLiveAPI_documentation/Live11.0.xml",
            "12.0.2": "https://structure-void.com/PythonLiveAPI_documentation/Live12.0.2.xml"
        }
        self.api_data: Dict[str, Dict[str, APIClass]] = {}

    def fetch_version_api(self, version: str, url: str) -> Dict[str, APIClass]:
        """获取特定版本的 API 信息"""
        print(f"📥 获取 Live {version} API 文档...")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 解析 XML
            root = ET.fromstring(response.content)
            classes = {}

            for cls in root.findall('.//class'):
                class_name = cls.get('name', 'Unknown')
                properties = set()
                methods = set()

                # 提取属性
                for prop in cls.findall('.//property'):
                    prop_name = prop.get('name')
                    if prop_name:
                        properties.add(prop_name)

                # 提取方法
                for method in cls.findall('.//method'):
                    method_name = method.get('name')
                    if method_name:
                        methods.add(method_name)

                classes[class_name] = APIClass(
                    name=class_name,
                    properties=properties,
                    methods=methods
                )

            print(f"  ✅ 找到 {len(classes)} 个类")
            return classes

        except Exception as e:
            print(f"  ❌ 错误: {e}")
            return {}

    def load_all_versions(self):
        """加载所有版本的 API"""
        for version, url in self.versions.items():
            self.api_data[version] = self.fetch_version_api(version, url)

    def compare_versions(self, version1: str, version2: str):
        """对比两个版本的差异"""
        print(f"\n{'='*60}")
        print(f"📊 对比 Live {version1} vs Live {version2}")
        print(f"{'='*60}")

        api1 = self.api_data.get(version1, {})
        api2 = self.api_data.get(version2, {})

        if not api1 or not api2:
            print("⚠️  无法对比 - 数据不完整")
            return

        # 新增的类
        new_classes = set(api2.keys()) - set(api1.keys())
        removed_classes = set(api1.keys()) - set(api2.keys())
        common_classes = set(api1.keys()) & set(api2.keys())

        print(f"\n🆕 新增的类 ({len(new_classes)}):")
        for cls in sorted(new_classes):
            print(f"  • {cls}")

        if removed_classes:
            print(f"\n❌ 移除的类 ({len(removed_classes)}):")
            for cls in sorted(removed_classes):
                print(f"  • {cls}")

        # 分析每个类的变化
        changes = defaultdict(lambda: {"new_props": [], "new_methods": [], "removed_props": [], "removed_methods": []})

        for cls_name in common_classes:
            cls1 = api1[cls_name]
            cls2 = api2[cls_name]

            new_props = cls2.properties - cls1.properties
            removed_props = cls1.properties - cls2.properties
            new_methods = cls2.methods - cls1.methods
            removed_methods = cls1.methods - cls2.methods

            if new_props or new_methods or removed_props or removed_methods:
                changes[cls_name]["new_props"] = sorted(new_props)
                changes[cls_name]["new_methods"] = sorted(new_methods)
                changes[cls_name]["removed_props"] = sorted(removed_props)
                changes[cls_name]["removed_methods"] = sorted(removed_methods)

        # 打印重要类的变化
        important_classes = ["Song", "Track", "Clip", "Device", "DeviceParameter", "Application", "Browser"]

        print(f"\n🔍 重要类的 API 变化:")
        for cls_name in important_classes:
            if cls_name in changes:
                change = changes[cls_name]
                print(f"\n  📦 {cls_name}:")

                if change["new_props"]:
                    print(f"    🆕 新属性 ({len(change['new_props'])}):")
                    for prop in change["new_props"][:10]:
                        print(f"      • {prop}")
                    if len(change["new_props"]) > 10:
                        print(f"      ... 还有 {len(change['new_props'])-10} 个")

                if change["new_methods"]:
                    print(f"    🆕 新方法 ({len(change['new_methods'])}):")
                    for method in change["new_methods"][:10]:
                        print(f"      • {method}()")
                    if len(change["new_methods"]) > 10:
                        print(f"      ... 还有 {len(change['new_methods'])-10} 个")

                if change["removed_props"]:
                    print(f"    ❌ 移除的属性: {', '.join(change['removed_props'])}")

                if change["removed_methods"]:
                    print(f"    ❌ 移除的方法: {', '.join(change['removed_methods'])}")

    def show_class_details(self, version: str, class_name: str):
        """显示特定类的详细信息"""
        print(f"\n{'='*60}")
        print(f"📖 {class_name} API (Live {version})")
        print(f"{'='*60}")

        api = self.api_data.get(version, {})
        cls = api.get(class_name)

        if not cls:
            print(f"⚠️  找不到类: {class_name}")
            return

        print(f"\n📊 属性 ({len(cls.properties)}):")
        for prop in sorted(cls.properties):
            print(f"  • {prop}")

        print(f"\n🔧 方法 ({len(cls.methods)}):")
        for method in sorted(cls.methods):
            print(f"  • {method}()")

    def analyze_live12_new_features(self):
        """分析 Live 12 的新功能"""
        print(f"\n{'='*60}")
        print(f"🎉 Live 12 新功能总结")
        print(f"{'='*60}")

        # 对比 11.0 和 12.0.2
        if "11.0" in self.api_data and "12.0.2" in self.api_data:
            self.compare_versions("11.0", "12.0.2")

        # 显示关键类的完整 API
        important_classes = ["Song", "Track", "Clip", "Device"]
        for cls_name in important_classes:
            self.show_class_details("12.0.2", cls_name)


def main():
    comparator = VersionComparator()

    print("🚀 Ableton Live API 版本对比工具")
    print("="*60)

    # 加载所有版本
    comparator.load_all_versions()

    # 分析 Live 12 新功能
    comparator.analyze_live12_new_features()

    # 交互式对比
    print("\n" + "="*60)
    print("💡 可用的版本:", ", ".join(comparator.versions.keys()))
    print("="*60)

    while True:
        print("\n选项:")
        print("  1. 对比两个版本")
        print("  2. 查看特定类的 API")
        print("  3. 退出")

        choice = input("\n请选择 (1-3): ").strip()

        if choice == "1":
            v1 = input("版本 1 (例如: 11.0): ").strip()
            v2 = input("版本 2 (例如: 12.0.2): ").strip()
            if v1 in comparator.versions and v2 in comparator.versions:
                comparator.compare_versions(v1, v2)
            else:
                print("⚠️  无效的版本号")

        elif choice == "2":
            version = input("版本 (例如: 12.0.2): ").strip()
            class_name = input("类名 (例如: Song): ").strip()
            if version in comparator.versions:
                comparator.show_class_details(version, class_name)
            else:
                print("⚠️  无效的版本号")

        elif choice == "3":
            break

        else:
            print("⚠️  无效的选择")

    print("\n👋 再见!")


if __name__ == "__main__":
    main()
