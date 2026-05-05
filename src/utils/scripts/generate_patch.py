#!/usr/bin/env python3
"""
补丁生成脚本
根据分析结果自动生成修复补丁
"""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.patch_manager import PatchManager
from src.utils.logger import LogAnalyzer

class PatchGenerator:
    """补丁生成器"""
    
    def __init__(self):
        self.patch_manager = PatchManager()
        self.log_analyzer = LogAnalyzer()
        
    def generate_from_log_analysis(self, days: int = 1) -> List[Dict]:
        """从日志分析生成补丁"""
        print(f"🔍 分析最近{days}天的日志...")
        
        # 分析日志
        analysis = self.log_analyzer.analyze_logs(days)
        
        if "error" in analysis:
            print(f"❌ 分析失败: {analysis['error']}")
            return []
        
        # 生成补丁
        patches = []
        recommendations = analysis.get("recommendations", [])
        
        for rec in recommendations:
            patch_data = self._recommendation_to_patch(rec, analysis)
            if patch_data:
                patches.append(patch_data)
        
        # 保存补丁文件
        created_patches = []
        for patch_data in patches:
            patch = self.patch_manager.create_patch_from_template(patch_data)
            if patch:
                created_patches.append(patch)
                print(f"✅ 生成补丁: {patch.id}")
        
        return created_patches
    
    def _recommendation_to_patch(self, recommendation: Dict, analysis: Dict) -> Dict:
        """将建议转换为补丁数据"""
        action = recommendation.get("action", "")
        
        patches_map = {
            "review_configuration": self._create_config_patch,
            "security_review": self._create_security_patch,
            "performance_optimization": self._create_performance_patch,
            "risk_assessment": self._create_risk_patch
        }
        
        if action in patches_map:
            return patches_map[action](recommendation, analysis)
        
        return None
    
    def _create_config_patch(self, recommendation: Dict, analysis: Dict) -> Dict:
        """创建配置修复补丁"""
        patch_id = f"config_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": patch_id,
            "description": f"修复配置问题: {recommendation.get('issue', '未知')}",
            "target_module": "src.core.decision_engine",
            "target_function": "DecisionEngine._load_providers",
            "priority": 80
        }
    
    def _create_security_patch(self, recommendation: Dict, analysis: Dict) -> Dict:
        """创建安全修复补丁"""
        patch_id = f"security_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": patch_id,
            "description": f"安全加固: {recommendation.get('issue', '未知')}",
            "target_module": "src.core.security_auditor",
            "target_function": "SecurityAuditor.validate_request",
            "priority": 90
        }
    
    def _create_performance_patch(self, recommendation: Dict, analysis: Dict) -> Dict:
        """创建性能优化补丁"""
        patch_id = f"performance_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": patch_id,
            "description": f"性能优化: {recommendation.get('issue', '未知')}",
            "target_module": "src.core.decision_engine",
            "target_function": "DecisionEngine._match_providers",
            "priority": 60
        }
    
    def _create_risk_patch(self, recommendation: Dict, analysis: Dict) -> Dict:
        """创建风险修复补丁"""
        patch_id = f"risk_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "id": patch_id,
            "description": f"风险修复: {recommendation.get('issue', '未知')}",
            "target_module": "src.core.risk_assessor",
            "target_function": "RiskAssessor.assess_risks",
            "priority": 70
        }
    
    def generate_custom_patch(self, 
                            issue_description: str,
                            target_module: str,
                            target_function: str,
                            fix_code: str) -> Dict:
        """生成自定义补丁"""
        patch_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建补丁文件
        patch_file = Path("patches") / f"{patch_id}.py"
        
        patch_content = f'''"""
补丁: {patch_id}
描述: {issue_description}
目标: {target_module}.{target_function}
生成时间: {datetime.now().isoformat()}
"""

--- METADATA ---
id: {patch_id}
description: {issue_description}
target_module: {target_module}
target_function: {target_function}
priority: 50
author: custom_generator
version: 1.0.0
created_at: {datetime.now().isoformat()}

--- CODE ---
def patched_function(*args, **kwargs):
    """
    自定义修复补丁
    问题: {issue_description}
    """
    # 原函数调用
    from {target_module} import {target_function} as original_function
    
    try:
        {fix_code}
    except Exception as e:
        # 如果补丁代码失败，回退到原函数
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"补丁执行失败: {{e}}")
        return original_function(*args, **kwargs)
'''
        
        with open(patch_file, 'w', encoding='utf-8') as f:
            f.write(patch_content)
        
        print(f"✅ 自定义补丁已生成: {patch_file}")
        
        return {
            "id": patch_id,
            "file": str(patch_file),
            "description": issue_description
        }
    
    def list_patches(self) -> List[Dict]:
        """列出所有补丁"""
        status = self.patch_manager.get_patch_status()
        
        patches = []
        for patch in status.get("applied_patches", []):
            patches.append({
                "id": patch["id"],
                "status": "✅ 已应用",
                "description": patch["description"],
                "target": patch["target"],
                "priority": patch["priority"]
            })
        
        for patch in status.get("pending_patches", []):
            patches.append({
                "id": patch["id"],
                "status": "⏳ 待应用",
                "description": patch["description"],
                "target": patch["target"],
                "priority": patch["priority"]
            })
        
        return patches
    
    def apply_all_pending(self) -> Dict:
        """应用所有待处理补丁"""
        print("🔄 应用所有待处理补丁...")
        results = self.patch_manager.apply_all_patches()
        
        success_count = sum(1 for r in results.values() if r)
        print(f"✅ 成功应用 {success_count}/{len(results)} 个补丁")
        
        return results

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="补丁生成与管理工具")
    parser.add_argument("command", choices=["generate", "list", "apply", "custom"],
                       help="命令: generate(从日志生成), list(列出补丁), apply(应用补丁), custom(自定义补丁)")
    parser.add_argument("--days", type=int, default=1,
                       help="分析最近多少天的日志 (默认: 1)")
    parser.add_argument("--issue", type=str,
                       help="问题描述 (用于custom命令)")
    parser.add_argument("--module", type=str,
                       help="目标模块 (用于custom命令)")
    parser.add_argument("--function", type=str,
                       help="目标函数 (用于custom命令)")
    parser.add_argument("--code", type=str,
                       help="修复代码 (用于custom命令)")
    
    args = parser.parse_args()
    
    generator = PatchGenerator()
    
    if args.command == "generate":
        patches = generator.generate_from_log_analysis(args.days)
        if patches:
            print(f"🎯 成功生成 {len(patches)} 个补丁")
        else:
            print("ℹ️ 未生成补丁")
    
    elif args.command == "list":
        patches = generator.list_patches()
        if patches:
            print(f"📋 共 {len(patches)} 个补丁:")
            for patch in patches:
                print(f"  {patch['status']} | {patch['id']}")
                print(f"      描述: {patch['description']}")
                print(f"      目标: {patch['target']}")
                print(f"      优先级: {patch['priority']}")
                print()
        else:
            print("📭 没有补丁")
    
    elif args.command == "apply":
        results = generator.apply_all_pending()
        for patch_id, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {status}: {patch_id}")
    
    elif args.command == "custom":
        if not all([args.issue, args.module, args.function, args.code]):
            print("❌ 自定义补丁需要所有参数: --issue, --module, --function, --code")
            return
        
        result = generator.generate_custom_patch(
            issue_description=args.issue,
            target_module=args.module,
            target_function=args.function,
            fix_code=args.code
        )
        print(f"📁 补丁文件: {result['file']}")

if __name__ == "__main__":
    main()