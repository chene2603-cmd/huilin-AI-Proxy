#!/usr/bin/env python3
"""
系统自检模块
验证所有依赖和环境配置
"""

import sys
import os
import json
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
import logging

class SystemSelfCheck:
    """系统自检类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.checks_passed = 0
        self.checks_failed = 0
        self.failures = []
        
    def run_checks(self) -> bool:
        """运行所有检查"""
        print("🔍 开始系统自检...\n")
        
        checks = [
            ("Python版本检查", self.check_python_version),
            ("依赖包检查", self.check_dependencies),
            ("配置文件检查", self.check_config_files),
            ("数据文件检查", self.check_data_files),
            ("日志目录检查", self.check_log_directory),
            ("补丁目录检查", self.check_patch_directory),
            ("权限检查", self.check_permissions)
        ]
        
        for check_name, check_func in checks:
            self._run_single_check(check_name, check_func)
        
        # 输出总结
        print(f"\n{'='*50}")
        print(f"自检完成: ✅ 通过 {self.checks_passed} 项 | ❌ 失败 {self.checks_failed} 项")
        
        if self.failures:
            print("\n失败项:")
            for failure in self.failures:
                print(f"  ❌ {failure}")
            print("\n💡 建议:")
            for suggestion in self._get_suggestions():
                print(f"  - {suggestion}")
        
        return self.checks_failed == 0
    
    def _run_single_check(self, name: str, func):
        """运行单个检查"""
        try:
            result, message = func()
            if result:
                print(f"✅ [{name}] {message}")
                self.checks_passed += 1
            else:
                print(f"❌ [{name}] {message}")
                self.checks_failed += 1
                self.failures.append(f"{name}: {message}")
        except Exception as e:
            print(f"⚠️  [{name}] 检查异常: {e}")
            self.checks_failed += 1
            self.failures.append(f"{name}: 检查异常 - {e}")
    
    def check_python_version(self) -> Tuple[bool, str]:
        """检查Python版本"""
        required_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version >= required_version:
            return True, f"Python {sys.version}"
        else:
            return False, f"需要Python {required_version[0]}.{required_version[1]}+，当前 {sys.version}"
    
    def check_dependencies(self) -> Tuple[bool, str]:
        """检查依赖包"""
        try:
            import yaml
            import requests
            return True, "基础依赖包正常"
        except ImportError as e:
            return False, f"缺少依赖包: {e.name}"
    
    def check_config_files(self) -> Tuple[bool, str]:
        """检查配置文件"""
        config_files = ["config.yaml", "data/providers.json", "data/risk_patterns.json"]
        
        missing_files = []
        for file in config_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if not missing_files:
            return True, "配置文件完整"
        else:
            return False, f"缺失配置文件: {', '.join(missing_files)}"
    
    def check_data_files(self) -> Tuple[bool, str]:
        """检查数据文件"""
        data_dir = Path("data")
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            
        # 创建默认数据文件
        default_files = {
            "providers.json": self._get_default_providers(),
            "risk_patterns.json": self._get_default_risk_patterns()
        }
        
        for filename, data in default_files.items():
            filepath = data_dir / filename
            if not filepath.exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True, "数据文件就绪"
    
    def _get_default_providers(self):
        """获取默认服务商数据"""
        return [
            {
                "id": "shiyunapi",
                "name": "诗云API",
                "type": "性能领导者",
                "tags": ["高并发", "全模型覆盖", "99.95% SLA", "企业级治理"],
                "suitable_for": ["企业核心业务", "Agent生产系统"],
                "sla": 0.9995,
                "cost_per_million": 8.5,
                "compliance": ["发票", "对公账户", "日志审计"],
                "risk_score": 85,
                "coverage": ["GPT-4", "GPT-5.5", "Claude-3", "Llama-4"],
                "min_cost": 1000
            }
        ]
    
    def _get_default_risk_patterns(self):
        """获取默认风险模式"""
        return {
            "data_leakage": {
                "name": "数据泄露风险",
                "description": "中转站可能记录、分析甚至出售用户数据",
                "severity": "HIGH",
                "mitigation": ["使用企业级服务商", "敏感信息脱敏", "后端代理调用"]
            }
        }
    
    def check_log_directory(self) -> Tuple[bool, str]:
        """检查日志目录"""
        log_dir = Path("logs")
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                return True, "日志目录已创建"
            except Exception as e:
                return False, f"无法创建日志目录: {e}"
        return True, "日志目录就绪"
    
    def check_patch_directory(self) -> Tuple[bool, str]:
        """检查补丁目录"""
        patch_dir = Path("patches")
        if not patch_dir.exists():
            try:
                patch_dir.mkdir(parents=True, exist_ok=True)
                # 创建README
                readme = patch_dir / "README.md"
                readme.write_text("# 补丁目录\n\n存放系统补丁文件\n")
                return True, "补丁目录已创建"
            except Exception as e:
                return False, f"无法创建补丁目录: {e}"
        return True, "补丁目录就绪"
    
    def check_permissions(self) -> Tuple[bool, str]:
        """检查权限"""
        try:
            # 测试写入权限
            test_file = Path("logs/test_permission.txt")
            test_file.write_text("test")
            test_file.unlink()
            return True, "文件系统权限正常"
        except Exception as e:
            return False, f"文件系统权限异常: {e}"
    
    def _get_suggestions(self) -> List[str]:
        """获取修复建议"""
        suggestions = []
        
        if "Python版本检查" in " ".join(self.failures):
            suggestions.append("请升级Python到3.8或更高版本")
        
        if "依赖包检查" in " ".join(self.failures):
            suggestions.append("运行: pip install -r requirements.txt")
        
        if "配置文件" in " ".join(self.failures):
            suggestions.append("检查config.yaml文件是否存在")
        
        if "权限" in " ".join(self.failures):
            suggestions.append("检查当前用户对项目目录的写入权限")
        
        if not suggestions:
            suggestions.append("查看详细错误信息并手动修复")
        
        return suggestions