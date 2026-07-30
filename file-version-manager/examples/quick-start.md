# 快速开始

## 在代码中使用

```python
from file_version_manager import FileVersionManager

# 创建管理器实例
manager = FileVersionManager()

# 场景1：直接创建新版本
new_path = manager.create_version("document.md")
# 输出: document_v1.md

# 再次创建
new_path = manager.create_version("document.md")
# 输出: document_v2.md

# 场景2：智能编辑（自动检测并创建版本）
edit_path = manager.smart_edit("document.md")
# 如果不存在：返回原路径
# 如果存在：创建新版本并返回新版本路径

# 场景3：列出所有版本
versions = manager.list_versions("document.md")
# 返回: [{"path": "...", "version": 0, "filename": "...", "size": ..., "mtime": ...}, ...]

# 场景4：查看最新版本
latest = manager.get_latest_version("document.md")
# 返回: {"path": "...", "version": 2, ...}

# 场景5：对比版本差异
diff = manager.diff_versions("document_v1.md", "document_v2.md")
```

## 命令行使用

```bash
# 创建新版本
python file_version_manager.py create document.md

# 列出所有版本
python file_version_manager.py list document.md

# 查看最新版本
python file_version_manager.py latest document.md

# 对比两个版本
python file_version_manager.py diff document_v1.md document_v2.md
```

## 在工作流中使用

当您需要修改文件时，使用 `smart_edit`：

```python
from file_version_manager import smart_edit

# 用户要求修改文件
# 系统自动处理版本逻辑
path = smart_edit("解析处理.md")

# 在 path 上执行修改
# 原文件保持不变
```
