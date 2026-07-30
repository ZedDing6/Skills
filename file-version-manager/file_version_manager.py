#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件版本管理器
在修改文件时自动保留历史版本，创建带版本号的副本（_v1, _v2, _v3...）
"""

import re
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime


class FileVersionManager:
    """文件版本管理器"""
    
    VERSION_PATTERN = re.compile(r'_v(\d+)$')
    MAX_VERSION = 999
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def _log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(message)
    
    def _extract_version(self, filename: str) -> int:
        """从文件名中提取版本号"""
        match = self.VERSION_PATTERN.search(filename)
        if match:
            return int(match.group(1))
        return 0
    
    def _get_base_name(self, file_path: str) -> Tuple[str, str, Path]:
        """获取文件的基本信息（不含版本号）"""
        path = Path(file_path)
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        # 如果文件名包含版本号，去除版本号
        match = self.VERSION_PATTERN.search(stem)
        if match:
            base_name = stem[:match.start()]
        else:
            base_name = stem
        
        return base_name, suffix, parent
    
    def list_versions(self, file_path: str) -> List[dict]:
        """
        列出文件的所有版本
        
        Returns:
            版本列表，每项包含：path, version, size, mtime
        """
        base_name, suffix, parent = self._get_base_name(file_path)
        
        versions = []
        
        # 检查原文件（v0）
        original = parent / f"{base_name}{suffix}"
        if original.exists():
            stat = original.stat()
            versions.append({
                "path": str(original),
                "version": 0,
                "filename": original.name,
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # 检查版本文件
        for item in parent.iterdir():
            if item.is_file() and item.suffix == suffix:
                match = self.VERSION_PATTERN.search(item.stem)
                if match:
                    # 检查基础名是否匹配
                    item_base = item.stem[:match.start()]
                    if item_base == base_name:
                        stat = item.stat()
                        versions.append({
                            "path": str(item),
                            "version": int(match.group(1)),
                            "filename": item.name,
                            "size": stat.st_size,
                            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
        
        # 按版本号排序
        versions.sort(key=lambda x: x["version"])
        return versions
    
    def get_latest_version(self, file_path: str) -> Optional[dict]:
        """获取最新版本"""
        versions = self.list_versions(file_path)
        if versions:
            return versions[-1]
        return None
    
    def get_next_version_path(self, file_path: str) -> str:
        """获取下一个版本的路径（但不创建文件）"""
        base_name, suffix, parent = self._get_base_name(file_path)
        versions = self.list_versions(file_path)
        
        if versions:
            max_version = max(v["version"] for v in versions)
            next_version = max_version + 1
        else:
            next_version = 1
        
        if next_version > self.MAX_VERSION:
            raise ValueError(f"版本号超过最大值 {self.MAX_VERSION}")
        
        new_path = parent / f"{base_name}_v{next_version}{suffix}"
        return str(new_path)
    
    def create_version(self, file_path: str, copy_from: Optional[str] = None) -> str:
        """
        创建新版本文件
        
        Args:
            file_path: 原文件路径
            copy_from: 从哪个文件复制（默认：最新版本）
        
        Returns:
            新文件路径
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        base_name, suffix, parent = self._get_base_name(file_path)
        versions = self.list_versions(file_path)
        
        # 计算下一个版本号
        if versions:
            max_version = max(v["version"] for v in versions)
            next_version = max_version + 1
        else:
            next_version = 1
        
        if next_version > self.MAX_VERSION:
            raise ValueError(f"版本号超过最大值 {self.MAX_VERSION}")
        
        # 生成新文件名
        new_filename = f"{base_name}_v{next_version}{suffix}"
        new_path = parent / new_filename
        
        # 确定复制源
        if copy_from:
            source = Path(copy_from)
        elif versions:
            # 复制最新版本
            latest = max(versions, key=lambda x: x["version"])
            source = Path(latest["path"])
        else:
            # 复制原文件
            source = path
        
        # 复制文件
        shutil.copy2(source, new_path)
        
        self._log(f"✅ 已创建版本副本: {new_filename}")
        self._log(f"   复制自: {source.name}")
        
        return str(new_path)
    
    def smart_edit(self, file_path: str) -> str:
        """
        智能编辑 - 自动创建版本并返回可编辑的文件路径
        
        使用场景：用户要求修改文件时，先调用此函数获取新版本路径
        """
        path = Path(file_path)
        
        if not path.exists():
            self._log(f"📝 文件不存在，将创建新文件: {path.name}")
            return file_path
        
        # 检查是否已有版本
        versions = self.list_versions(file_path)
        
        if len(versions) <= 1:
            # 只有原文件或没有文件，创建v1
            self._log(f"📝 检测到原文件，创建版本副本...")
        else:
            # 已有版本，创建新版本
            self._log(f"📝 检测到已有 {len(versions)-1} 个版本，创建新版本...")
        
        # 创建新版本
        new_path = self.create_version(file_path)
        
        # 输出版本链信息
        self._print_version_chain(file_path)
        
        return new_path
    
    def _print_version_chain(self, file_path: str):
        """打印版本链"""
        versions = self.list_versions(file_path)
        if len(versions) > 1:
            self._log("\n📋 版本历史:")
            for v in versions:
                marker = " ← 当前" if v == versions[-1] else ""
                if v["version"] == 0:
                    self._log(f"   v0: {v['filename']} (原始){marker}")
                else:
                    self._log(f"   v{v['version']}: {v['filename']}{marker}")
    
    def diff_versions(self, version1: str, version2: str) -> str:
        """
        比较两个版本的差异
        
        Returns:
            差异报告文本
        """
        path1 = Path(version1)
        path2 = Path(version2)
        
        if not path1.exists():
            raise FileNotFoundError(f"文件不存在: {version1}")
        if not path2.exists():
            raise FileNotFoundError(f"文件不存在: {version2}")
        
        # 读取文件内容
        with open(path1, 'r', encoding='utf-8', errors='ignore') as f:
            content1 = f.read()
        with open(path2, 'r', encoding='utf-8', errors='ignore') as f:
            content2 = f.read()
        
        # 简单对比
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        from difflib import unified_diff
        diff = list(unified_diff(lines1, lines2, 
                                  fromfile=path1.name, 
                                  tofile=path2.name,
                                  lineterm=''))
        
        return '\n'.join(diff)
    
    def clean_versions(self, file_path: str, keep_last: int = 5) -> List[str]:
        """
        清理旧版本，只保留最近N个
        
        Args:
            file_path: 原文件路径
            keep_last: 保留的最近版本数
        
        Returns:
            删除的文件列表
        """
        versions = self.list_versions(file_path)
        
        if len(versions) <= keep_last:
            return []
        
        # 保留原文件和最近N个版本
        to_keep = set()
        to_keep.add(versions[0]["path"])  # 原文件
        for v in versions[-keep_last:]:
            to_keep.add(v["path"])
        
        deleted = []
        for v in versions:
            if v["path"] not in to_keep:
                Path(v["path"]).unlink()
                deleted.append(v["path"])
                self._log(f"🗑️  已删除旧版本: {v['filename']}")
        
        return deleted


# 便捷函数
def create_version(file_path: str) -> str:
    """创建版本副本的便捷函数"""
    manager = FileVersionManager()
    return manager.create_version(file_path)


def smart_edit(file_path: str) -> str:
    """智能编辑的便捷函数"""
    manager = FileVersionManager()
    return manager.smart_edit(file_path)


def list_versions(file_path: str) -> List[dict]:
    """列出版本的便捷函数"""
    manager = FileVersionManager()
    return manager.list_versions(file_path)


# 命令行接口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python file_version_manager.py create <file>     - 创建新版本")
        print("  python file_version_manager.py list <file>       - 列出所有版本")
        print("  python file_version_manager.py latest <file>     - 查看最新版本")
        print("  python file_version_manager.py diff <v1> <v2>      - 对比两个版本")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = FileVersionManager()
    
    if command == "create":
        if len(sys.argv) < 3:
            print("错误: 请指定文件路径")
            sys.exit(1)
        new_path = manager.create_version(sys.argv[2])
        print(f"\n✅ 新版本: {new_path}")
    
    elif command == "list":
        if len(sys.argv) < 3:
            print("错误: 请指定文件路径")
            sys.exit(1)
        versions = manager.list_versions(sys.argv[2])
        print(f"\n📋 版本历史 ({len(versions)} 个版本):")
        for v in versions:
            size_kb = v["size"] / 1024
            print(f"  v{v['version']}: {v['filename']} ({size_kb:.1f} KB) - {v['mtime']}")
    
    elif command == "latest":
        if len(sys.argv) < 3:
            print("错误: 请指定文件路径")
            sys.exit(1)
        latest = manager.get_latest_version(sys.argv[2])
        if latest:
            print(f"\n✅ 最新版本: {latest['path']}")
        else:
            print("\n❌ 未找到版本")
    
    elif command == "diff":
        if len(sys.argv) < 4:
            print("错误: 请指定两个版本文件")
            sys.exit(1)
        diff = manager.diff_versions(sys.argv[2], sys.argv[3])
        print(diff)
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
