#!/usr/bin/env python3
"""
补丁管理系统
支持动态加载和热修复
"""

import importlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import logging

class Patch:
    """补丁类"""
    
    def __init__(self, patch_id: str, description: str, 
                 target_module: str, target_function: str,
                 patch_code: str, priority: int = 0,
                 author: str = "system", version: str = "1.0.0"):
        self.id = patch_id
        self.description = description
        self.target_module = target_module
        self.target_function = target_function
        self.patch_code = patch_code
        self.priority = priority
        self.author = author
        self.version = version
        self.created_at = datetime.now()
        self.applied = False
        self.original_function = None
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """计算补丁代码的校验和"""
        content = f"{self.target_module}.{self.target_function}:{self.patch_code}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def validate(self) -> bool:
        """验证补丁代码"""
        try:
            # 尝试编译代码
            compile(self.patch_code, f"<patch:{self.id}>", 'exec')
            return True
        except SyntaxError as e:
            logging.error(f"补丁语法错误 {self.id}: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"Patch({self.id}, target={self.target_module}.{self.target_function}, priority={self.priority})"

class PatchManager:
    """补丁管理器"""
    
    def __init__(self, patch_dir: str = "patches"):
        self.patch_dir = Path(patch_dir)
        self.patch_dir.mkdir(exist_ok=True)
        self.patches: Dict[str, Patch] = {}
        self.logger = logging.getLogger(__name__)
        self._init_patch_registry()
    
    def _init_patch_registry(self):
        """初始化补丁注册表"""
        self.registry_file = self.patch_dir / "registry.json"
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                for patch_data in registry.get("patches", []):
                    patch = Patch(
                        patch_id=patch_data["id"],
                        description=patch_data["description"],
                        target_module=patch_data["target_module"],
                        target_function=patch_data["target_function"],
                        patch_code=patch_data["patch_code"],
                        priority=patch_data.get("priority", 0),
                        author=patch_data.get("author", "system"),
                        version=patch_data.get("version", "1.0.0")
                    )
                    patch.applied = patch_data.get("applied", False)
                    patch.created_at = datetime.fromisoformat(patch_data["created_at"])
                    self.patches[patch.id] = patch
        else:
            self._save_registry()
    
    def _save_registry(self):
        """保存补丁注册表"""
        registry = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "patches": []
        }
        
        for patch in self.patches.values():
            registry["patches"].append({
                "id": patch.id,
                "description": patch.description,
                "target_module": patch.target_module,
                "target_function": patch.target_function,
                "patch_code": patch.patch_code,
                "priority": patch.priority,
                "author": patch.author,
                "version": patch.version,
                "applied": patch.applied,
                "created_at": patch.created_at.isoformat(),
                "checksum": patch.checksum
            })
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
    
    def load_patch_file(self, filepath: str) -> Optional[Patch]:
        """从文件加载补丁"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析补丁文件
            lines = content.split('\n')
            metadata = {}
            code_lines = []
            in_metadata = False
            in_code = False
            
            for line in lines:
                if line.strip() == "--- METADATA ---":
                    in_metadata = True
                    in_code = False
                elif line.strip() == "--- CODE ---":
                    in_metadata = False
                    in_code = True
                elif in_metadata and ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
                elif in_code:
                    code_lines.append(line)
                elif line.strip().startswith("#"):
                    # 注释行
                    continue
            
            patch_code = '\n'.join(code_lines)
            
            if not all(k in metadata for k in ["id", "description", "target_module", "target_function"]):
                self.logger.error(f"补丁文件缺少必要元数据: {filepath}")
                return None
            
            patch = Patch(
                patch_id=metadata["id"],
                description=metadata["description"],
                target_module=metadata["target_module"],
                target_function=metadata["target_function"],
                patch_code=patch_code,
                priority=int(metadata.get("priority", 0)),
                author=metadata.get("author", "system"),
                version=metadata.get("version", "1.0.0")
            )
            
            if patch.validate():
                return patch
            else:
                self.logger.error(f"补丁验证失败: {metadata['id']}")
                return None
                
        except Exception as e:
            self.logger.error(f"加载补丁文件失败 {filepath}: {e}")
            return None
    
    def load_all_patches(self) -> List[Patch]:
        """加载所有补丁文件"""
        patch_files = list(self.patch_dir.glob("*.py"))
        loaded_patches = []
        
        for patch_file in patch_files:
            if patch_file.name.startswith("_"):
                continue
                
            patch = self.load_patch_file(str(patch_file))
            if patch:
                if patch.id in self.patches:
                    # 检查是否需要更新
                    existing = self.patches[patch.id]
                    if existing.checksum != patch.checksum:
                        self.logger.info(f"发现补丁更新: {patch.id}")
                        self.patches[patch.id] = patch
                        loaded_patches.append(patch)
                else:
                    self.patches[patch.id] = patch
                    loaded_patches.append(patch)
        
        # 按优先级排序
        loaded_patches.sort(key=lambda x: x.priority, reverse=True)
        
        # 保存注册表
        self._save_registry()
        
        self.logger.info(f"加载了 {len(loaded_patches)} 个补丁")
        return loaded_patches
    
    def apply_patch(self, patch: Patch) -> bool:
        """应用补丁"""
        if patch.applied:
            self.logger.info(f"补丁已应用: {patch.id}")
            return True
        
        try:
            # 导入目标模块
            module = importlib.import_module(patch.target_module)
            
            # 获取目标函数
            target_func = getattr(module, patch.target_function)
            patch.original_function = target_func
            
            # 创建补丁函数
            exec_globals = {
                "__name__": f"patched_{patch.target_module}",
                "original_function": target_func
            }
            
            # 执行补丁代码
            exec(patch.patch_code, exec_globals)
            
            # 获取补丁函数
            patched_func = exec_globals.get("patched_function")
            if not patched_func:
                self.logger.error(f"补丁未定义 patched_function: {patch.id}")
                return False
            
            # 替换原函数
            setattr(module, patch.target_function, patched_func)
            
            patch.applied = True
            self._save_registry()
            
            self.logger.info(f"✅ 补丁应用成功: {patch.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 应用补丁失败 {patch.id}: {e}")
            return False
    
    def apply_all_patches(self) -> Dict[str, bool]:
        """应用所有补丁"""
        results = {}
        
        # 按优先级排序
        sorted_patches = sorted(self.patches.values(), 
                              key=lambda x: x.priority, 
                              reverse=True)
        
        for patch in sorted_patches:
            if not patch.applied:
                success = self.apply_patch(patch)
                results[patch.id] = success
        
        return results
    
    def revert_patch(self, patch_id: str) -> bool:
        """回滚补丁"""
        if patch_id not in self.patches:
            self.logger.error(f"补丁不存在: {patch_id}")
            return False
        
        patch = self.patches[patch_id]
        if not patch.applied or not patch.original_function:
            self.logger.info(f"补丁未应用: {patch_id}")
            return True
        
        try:
            # 导入目标模块
            module = importlib.import_module(patch.target_module)
            
            # 恢复原函数
            setattr(module, patch.target_function, patch.original_function)
            
            patch.applied = False
            patch.original_function = None
            self._save_registry()
            
            self.logger.info(f"↩️ 补丁回滚成功: {patch_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"回滚补丁失败 {patch_id}: {e}")
            return False
    
    def get_patch_status(self) -> Dict[str, Any]:
        """获取补丁状态"""
        applied = []
        pending = []
        
        for patch in self.patches.values():
            status = {
                "id": patch.id,
                "description": patch.description,
                "target": f"{patch.target_module}.{patch.target_function}",
                "priority": patch.priority,
                "applied": patch.applied,
                "created_at": patch.created_at.isoformat()
            }
            
            if patch.applied:
                applied.append(status)
            else:
                pending.append(status)
        
        return {
            "total": len(self.patches),
            "applied": len(applied),
            "pending": len(pending),
            "applied_patches": applied,
            "pending_patches": pending
        }
    
    def generate_patch_template(self, patch_id: str, 
                              description: str,
                              target_module: str,
                              target_function: str) -> str:
        """生成补丁模板"""
        template = f'''"""
补丁: {patch_id}
描述: {description}
目标: {target_module}.{target_function}
优先级: 0 (0-100, 越高越先应用)
"""

--- METADATA ---
id: {patch_id}
description: {description}
target_module: {target_module}
target_function: {target_function}
priority: 0
author: system
version: 1.0.0
created_at: {datetime.now().isoformat()}

--- CODE ---
def patched_function(*args, **kwargs):
    """
    补丁函数
    注意: 必须命名为 patched_function
    可以通过 original_function 调用原函数
    """
    # 在这里编写补丁逻辑
    
    # 示例: 在调用前后添加日志
    print(f"调用 {{target_function}} 前")
    
    # 调用原函数
    result = original_function(*args, **kwargs)
    
    print(f"调用 {{target_function}} 后")
    
    return result
'''
        return template
    
    def create_patch_from_template(self, template_data: Dict[str, Any]) -> Optional[Patch]:
        """从模板数据创建补丁"""
        try:
            # 生成补丁文件
            patch_file = self.patch_dir / f"{template_data['id']}.py"
            
            with open(patch_file, 'w', encoding='utf-8') as f:
                template = self.generate_patch_template(
                    patch_id=template_data['id'],
                    description=template_data['description'],
                    target_module=template_data['target_module'],
                    target_function=template_data['target_function']
                )
                f.write(template)
            
            # 加载并验证
            patch = self.load_patch_file(str(patch_file))
            if patch:
                self.patches[patch.id] = patch
                self._save_registry()
                return patch
            
        except Exception as e:
            self.logger.error(f"创建补丁失败: {e}")
        
        return None

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 创建一个 PatchManager 实例
    pm = PatchManager(patch_dir="./patches")
    
    # 生成一个补丁模板并保存
    template = pm.generate_patch_template(
        patch_id="test_patch_1",
        description="测试补丁",
        target_module="math",
        target_function="sqrt"
    )
    with open("./patches/test_patch_1.py", "w", encoding="utf-8") as f:
        f.write(template)
    
    # 加载所有补丁
    pm.load_all_patches()
    
    # 查看补丁状态
    status = pm.get_patch_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # 应用所有补丁
    # results = pm.apply_all_patches()
    # print(results)
    
    # 回滚补丁
    # pm.revert_patch("test_patch_1")