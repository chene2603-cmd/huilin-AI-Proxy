#!/usr/bin/env python3
"""
AI中转站选型辅助与风险审计系统 - 主入口
版本: 1.0.0
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import setup_logger
from src.cli.interface import CLIInterface
from src.utils.patch_manager import PatchManager
from src.core.self_check import SystemSelfCheck

def main():
    """主函数"""
    try:
        # 1. 设置日志
        logger = setup_logger()
        logger.info("=" * 60)
        logger.info("AI中转站选型辅助系统启动")
        logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 2. 系统自检
        logger.info("🚀 开始系统自检...")
        self_check = SystemSelfCheck()
        if not self_check.run_checks():
            logger.error("❌ 系统自检失败，请检查环境配置")
            sys.exit(1)
        logger.info("✅ 系统自检通过")
        
        # 3. 加载补丁
        logger.info("🔄 加载系统补丁...")
        patch_manager = PatchManager()
        applied_patches = patch_manager.load_all_patches()
        logger.info(f"✅ 成功加载 {len(applied_patches)} 个补丁")
        
        # 4. 启动CLI界面
        logger.info("🚀 启动交互界面...")
        cli = CLIInterface()
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断操作，系统正常退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 系统启动失败: {e}")
        logger.error(f"系统启动失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()