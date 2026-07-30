---
name: file-version-manager
description: 文件版本管理技能 - 在修改文件时自动保留历史版本，创建带版本号的副本（_v1, _v2, _v3...）
license: MIT
display_name: 文件版本管理器
description_zh: 在修改文件时自动创建版本副本，保留历史版本
aliases: [版本管理, 文件备份, 历史版本, file backup, version control]
---

# File Version Manager

## 技能概述

本技能用于管理文件版本历史。当需要修改已有文件时，自动创建带版本号的副本（如 `_v1.md`, `_v2.md`），确保原始文件不被覆盖，同时保留完整的修改历史。

## 适用场景

- 需要反复修改和迭代文档/代码
- 需要保留每个修改版本作为备份
- 需要对比不同版本的差异
- 需要回溯到之前的版本

## 核心功能

### 1. 自动版本检测

当用户要求修改文件时：
1. 首先检测目标文件是否已存在
2. 如果存在，查找当前最高版本号
3. 自动创建新版本（_vN）
4. 在新版本上进行修改

### 2. 版本命名规则

```
原文件名: 解析处理.md
版本文件: 解析处理_v1.md, 解析处理_v2.md, 解析处理_v3.md...

原文件名: report.docx
版本文件: report_v1.docx, report_v2.docx...
```

### 3. 版本链管理

- 每个新版本都基于最新版本创建
- 版本号连续递增（无跳号）
- 保留所有历史版本
- 可随时回溯到任意版本

## 使用方式

### 方式1：自动版本保护（推荐）

当你需要对文件进行修改时，系统会自动：

1. 检查文件是否存在
2. 如果存在，创建版本副本
3. 在新副本上执行修改
4. 告知用户创建了哪个版本

### 方式2：手动创建版本

使用Python脚本手动管理版本：

```python
from file_version_manager import FileVersionManager

manager = FileVersionManager()

# 创建新版本文件
new_path = manager.create_version("C:/work/document.md")
# 返回: C:/work/document_v1.md

# 再次创建
new_path = manager.create_version("C:/work/document.md")
# 返回: C:/work/document_v2.md

# 获取当前最高版本
latest = manager.get_latest_version("C:/work/document.md")
# 返回: C:/work/document_v2.md

# 列出所有版本
versions = manager.list_versions("C:/work/document.md")
# 返回: ["document.md", "document_v1.md", "document_v2.md"]
```

### 方式3：命令行使用

```bash
# 创建新版本
python -m file_version_manager create document.md

# 查看最新版本
python -m file_version_manager latest document.md

# 列出所有版本
python -m file_version_manager list document.md

# 对比两个版本差异
python -m file_version_manager diff document_v1.md document_v2.md
```

## 工作流程

### 场景：用户要求修改已有文件

```
用户: "帮我修改 解析处理.md 文件"

系统处理流程:
1. 检查 解析处理.md 是否存在 → 存在
2. 查找当前版本 → 无版本文件（首次修改）
3. 创建 解析处理_v1.md（复制原文件内容）
4. 在 解析处理_v1.md 上执行修改
5. 告知用户: "已在 解析处理_v1.md 完成修改，原文件保持不变"

第二次修改:
1. 检查 解析处理.md 是否存在 → 存在
2. 查找当前版本 → 已有 _v1
3. 创建 解析处理_v2.md（复制 _v1 内容）
4. 在 解析处理_v2.md 上执行修改
5. 告知用户: "已在 解析处理_v2.md 完成修改"
```

## 输出规范

每次创建新版本时，系统会输出：

```
✅ 版本管理
- 原文件: document.md（保持不变）
- 新版本: document_v1.md（在此修改）
- 版本历史: document.md → document_v1.md
```

## 示例

### 示例1：首次修改

**用户请求**: "修改 report.md，添加摘要部分"

**系统响应**:
```
检测到 report.md 已存在，创建版本副本...
✅ 已创建新版本: report_v1.md

正在 report_v1.md 上执行修改...
✅ 修改完成！

版本状态:
- 原始版本: report.md（首次创建时的版本）
- 当前版本: report_v1.md（已添加摘要）
```

### 示例2：迭代修改

**用户请求**: "继续修改 report，添加结论"

**系统响应**:
```
检测到已有版本 v1，创建新版本...
✅ 已创建新版本: report_v2.md

正在 report_v2.md 上执行修改...
✅ 修改完成！

版本链:
- v0: report.md（原始）
- v1: report_v1.md（添加摘要）
- v2: report_v2.md（添加结论）← 当前
```

### 示例3：查看版本历史

**用户请求**: "查看 report 的所有版本"

**系统响应**:
```
report.md 的版本历史:
├── report.md      (v0) - 2026-07-30 10:00 创建
├── report_v1.md   (v1) - 2026-07-30 10:30 修改：添加摘要
└── report_v2.md   (v2) - 2026-07-30 11:00 修改：添加结论

当前最新版本: report_v2.md
```

## 注意事项

1. **原文件永不修改** - 原文件始终作为v0保留
2. **版本连续递增** - 不会跳过版本号
3. **自动检测** - 无需手动指定版本操作
4. **路径支持** - 支持绝对路径和相对路径
5. **跨平台** - 支持Windows和Unix路径

## 技术实现

核心逻辑：
```python
import re
import os
import shutil
from pathlib import Path

class FileVersionManager:
    def create_version(self, file_path: str) -> str:
        """创建新版本文件，返回新文件路径"""
        path = Path(file_path)
        base_name = path.stem  # 不含扩展名的文件名
        suffix = path.suffix   # 扩展名
        parent = path.parent
        
        # 查找当前最高版本
        version = self._get_next_version(parent, base_name, suffix)
        
        # 生成新文件名
        if version == 0:
            new_name = f"{base_name}_v1{suffix}"
        else:
            new_name = f"{base_name}_v{version + 1}{suffix}"
        
        new_path = parent / new_name
        
        # 复制内容
        if version == 0:
            # 第一次：复制原文件
            shutil.copy2(file_path, new_path)
        else:
            # 第N次：复制最新版本
            latest = self._get_latest_version_file(parent, base_name, suffix)
            shutil.copy2(latest, new_path)
        
        return str(new_path)
```

## 约束与限制

- 最大支持版本号：999（v999），超过需要手动归档
- 版本文件与原文件必须在同一目录
- 不支持文件夹的版本管理（仅针对单个文件）
