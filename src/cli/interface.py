#!/usr/bin/env python3
"""
CLI交互界面
提供彩色、交互式的命令行界面
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import json
import yaml
from enum import Enum
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.decision_engine import DecisionEngine, UserRequirements, UseCase, ComplianceRequirement
from src.utils.logger import analyze_logs_command
from scripts.generate_patch import PatchGenerator

class Colors:
    """颜色定义"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class CLIInterface:
    """CLI交互界面"""
    
    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.colors = Colors()
        self.current_requirements = None
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """打印页眉"""
        self.clear_screen()
        print(f"{self.colors.BLUE}{'='*60}{self.colors.ENDC}")
        print(f"{self.colors.CYAN}{self.colors.BOLD}🤖 AI中转站选型辅助与风险审计系统{self.colors.ENDC}")
        print(f"{self.colors.BLUE}版本: 1.0.0 | 时间: 2026-05-05{self.colors.ENDC}")
        print(f"{self.colors.BLUE}{'='*60}{self.colors.ENDC}\n")
    
    def print_menu(self, options: List[Dict], title: str = "主菜单"):
        """打印菜单"""
        self.print_header()
        print(f"{self.colors.YELLOW}📋 {title}{self.colors.ENDC}\n")
        
        for i, option in enumerate(options, 1):
            emoji = option.get("emoji", "◦")
            print(f"  {self.colors.GREEN}{i}. {emoji} {option['name']}{self.colors.ENDC}")
            if "description" in option:
                print(f"     {option['description']}")
            print()
        
        print(f"{self.colors.BLUE}{'-'*60}{self.colors.ENDC}")
    
    def get_choice(self, max_choice: int) -> int:
        """获取用户选择"""
        while True:
            try:
                choice = input(f"\n{self.colors.CYAN}👉 请选择 (1-{max_choice}, 0返回上级): {self.colors.ENDC}")
                if choice == "0":
                    return 0
                
                choice = int(choice)
                if 1 <= choice <= max_choice:
                    return choice
                else:
                    print(f"{self.colors.RED}❌ 请输入 1-{max_choice} 之间的数字{self.colors.ENDC}")
            except ValueError:
                print(f"{self.colors.RED}❌ 请输入有效的数字{self.colors.ENDC}")
    
    def show_loading(self, message: str, duration: int = 2):
        """显示加载动画"""
        print(f"\n{self.colors.CYAN}{message}", end="", flush=True)
        
        for _ in range(duration * 2):
            time.sleep(0.5)
            print(".", end="", flush=True)
        
        print(f"{self.colors.ENDC}")
    
    def main_menu(self):
        """主菜单"""
        options = [
            {
                "name": "开始选型分析",
                "emoji": "🚀",
                "description": "根据您的需求匹配最佳AI中转站"
            },
            {
                "name": "风险评估报告",
                "emoji": "⚠️",
                "description": "查看已知风险和安全建议"
            },
            {
                "name": "服务商对比",
                "emoji": "📊",
                "description": "对比不同服务商的优劣"
            },
            {
                "name": "日志分析",
                "emoji": "📈",
                "description": "分析系统日志和生成补丁"
            },
            {
                "name": "系统设置",
                "emoji": "⚙️",
                "description": "系统配置和管理"
            },
            {
                "name": "退出系统",
                "emoji": "👋",
                "description": "安全退出程序"
            }
        ]
        
        while True:
            self.print_menu(options, "主菜单")
            choice = self.get_choice(len(options))
            
            if choice == 0:
                continue
            elif choice == 1:
                self.start_analysis()
            elif choice == 2:
                self.risk_report()
            elif choice == 3:
                self.provider_comparison()
            elif choice == 4:
                self.log_analysis()
            elif choice == 5:
                self.system_settings()
            elif choice == 6:
                self.exit_system()
                break
    
    def start_analysis(self):
        """开始选型分析"""
        self.show_loading("正在准备选型向导")
        
        # 收集需求
        requirements = self.collect_requirements()
        
        if requirements is None:
            return  # 用户取消
        
        self.current_requirements = requirements
        
        # 开始分析
        self.show_loading("正在分析需求并匹配服务商", 3)
        
        try:
            # 运行决策引擎
            result = self.decision_engine.assess_requirements(requirements)
            
            # 显示结果
            self.display_results(result)
            
            # 询问是否保存
            self.ask_save_result(result)
            
        except Exception as e:
            print(f"\n{self.colors.RED}❌ 分析过程中发生错误: {e}{self.colors.ENDC}")
            input(f"\n{self.colors.YELLOW}按回车键返回...{self.colors.ENDC}")
    
    def collect_requirements(self) -> Optional[UserRequirements]:
        """收集用户需求"""
        steps = [
            ("使用场景", self.ask_use_case),
            ("合规需求", self.ask_compliance),
            ("模型需求", self.ask_models),
            ("预算限制", self.ask_budget),
            ("性能要求", self.ask_performance),
            ("安全等级", self.ask_security)
        ]
        
        requirements_data = {}
        
        for i, (step_name, step_func) in enumerate(steps, 1):
            self.print_header()
            print(f"{self.colors.YELLOW}📝 需求收集 ({i}/{len(steps)}): {step_name}{self.colors.ENDC}\n")
            
            # 显示进度条
            progress = int(i / len(steps) * 50)
            print(f"{self.colors.BLUE}[{'█'*progress}{'░'*(50-progress)}] {i}/{len(steps)}{self.colors.ENDC}\n")
            
            # 执行步骤函数
            result = step_func()
            if result is None:  # 用户取消
                return None
            
            requirements_data.update(result)
        
        # 创建需求对象
        try:
            req = UserRequirements(
                use_case=requirements_data["use_case"],
                compliance_needs=requirements_data.get("compliance_needs", []),
                models_needed=requirements_data.get("models_needed", []),
                budget=requirements_data.get("budget"),
                monthly_tokens=requirements_data.get("monthly_tokens"),
                sla_requirement=requirements_data.get("sla_requirement", 0.99),
                latency_requirement=requirements_data.get("latency_requirement", 1000),
                security_level=requirements_data.get("security_level", "medium")
            )
            return req
        except Exception as e:
            print(f"{self.colors.RED}❌ 创建需求对象失败: {e}{self.colors.ENDC}")
            return None
    
    def ask_use_case(self) -> Optional[Dict]:
        """询问使用场景"""
        use_cases = [
            ("核心生产业务", UseCase.CORE_PRODUCTION, "企业核心业务系统，对稳定性和安全性要求极高"),
            ("企业级Agent系统", UseCase.ENTERPRISE_AGENT, "智能Agent生产环境，需要高并发和低延迟"),
            ("中小企业业务", UseCase.SME_BUSINESS, "中小企业日常业务，注重成本效益和合规"),
            ("个人开发者/学生", UseCase.PERSONAL_DEV, "学习、实验或个人项目，预算有限"),
            ("研究实验", UseCase.RESEARCH_EXP, "学术研究或技术实验，需要灵活配置"),
            ("出海业务", UseCase.OVERSEAS, "业务涉及海外，需要GDPR等国际合规"),
            ("开源模型研究", UseCase.OPEN_SOURCE, "专注于开源模型的本地化部署和调优")
        ]
        
        print(f"{self.colors.CYAN}请选择主要使用场景:{self.colors.ENDC}\n")
        
        for i, (name, use_case, desc) in enumerate(use_cases, 1):
            print(f"  {self.colors.GREEN}{i}. {name}{self.colors.ENDC}")
            print(f"     {desc}\n")
        
        choice = self.get_choice(len(use_cases))
        if choice == 0:
            return None
        
        selected_use_case = use_cases[choice-1][1]
        
        return {"use_case": selected_use_case}
    
    def ask_compliance(self) -> Optional[Dict]:
        """询问合规需求"""
        compliance_options = [
            ("需要发票", ComplianceRequirement.INVOICE, "需要正规增值税发票"),
            ("对公账户", ComplianceRequirement.CORPORATE_ACCOUNT, "需要支持对公账户付款"),
            ("GDPR合规", ComplianceRequirement.GDPR, "业务涉及欧盟，需要GDPR合规"),
            ("数据本地化", ComplianceRequirement.DATA_LOCALIZATION, "数据需要存储在中国境内"),
            ("日志审计", ComplianceRequirement.LOG_AUDIT, "需要完整的操作日志审计"),
            ("等保三级", ComplianceRequirement.SL3_CERT, "需要通过等保三级认证")
        ]
        
        print(f"{self.colors.CYAN}请选择合规需求 (可多选):{self.colors.ENDC}")
        print(f"{self.colors.YELLOW}输入数字选择，多个数字用空格分隔，0为完成{self.colors.ENDC}\n")
        
        for i, (name, req, desc) in enumerate(compliance_options, 1):
            print(f"  [{i}] {name}")
            print(f"      {desc}\n")
        
        selected = []
        while True:
            try:
                choices = input(f"{self.colors.CYAN}👉 请选择: {self.colors.ENDC}")
                if choices.strip() == "0":
                    break
                
                for choice in choices.split():
                    idx = int(choice) - 1
                    if 0 <= idx < len(compliance_options):
                        selected.append(compliance_options[idx][1])
                    else:
                        print(f"{self.colors.RED}❌ 无效选择: {choice}{self.colors.ENDC}")
                
                if selected:
                    print(f"\n{self.colors.GREEN}✅ 已选择: {len(selected)} 项{self.colors.ENDC}")
                    break
                    
            except ValueError:
                print(f"{self.colors.RED}❌ 请输入有效的数字{self.colors.ENDC}")
        
        return {"compliance_needs": selected}
    
    def ask_models(self) -> Optional[Dict]:
        """询问模型需求"""
        common_models = [
            ("GPT-5.5", "OpenAI最新模型"),
            ("GPT-4", "OpenAI GPT-4系列"),
            ("Claude-3", "Anthropic Claude 3系列"),
            ("Gemini-2.0", "Google Gemini 2.0"),
            ("Llama-4", "Meta最新开源模型"),
            ("Qwen-3.0", "阿里通义千问3.0"),
            ("DeepSeek-V3", "深度求索最新模型"),
            ("智谱GLM-5", "智谱AI GLM-5")
        ]
        
        print(f"{self.colors.CYAN}请选择需要的模型 (可多选):{self.colors.ENDC}")
        print(f"{self.colors.YELLOW}输入数字选择，多个数字用空格分隔，0为完成{self.colors.ENDC}\n")
        
        for i, (name, desc) in enumerate(common_models, 1):
            print(f"  [{i}] {name:20} - {desc}")
        
        print(f"\n  [{len(common_models)+1}] 自定义模型")
        
        selected = []
        while True:
            try:
                choices = input(f"{self.colors.CYAN}👉 请选择: {self.colors.ENDC}")
                if choices.strip() == "0":
                    break
                
                for choice in choices.split():
                    idx = int(choice) - 1
                    if idx == len(common_models):  # 自定义选项
                        custom = input(f"{self.colors.CYAN}请输入自定义模型名(用逗号分隔): {self.colors.ENDC}")
                        if custom:
                            selected.extend([m.strip() for m in custom.split(",")])
                    elif 0 <= idx < len(common_models):
                        selected.append(common_models[idx][0])
                    else:
                        print(f"{self.colors.RED}❌ 无效选择: {choice}{self.colors.ENDC}")
                
                if selected:
                    # 去重
                    selected = list(dict.fromkeys(selected))
                    print(f"\n{self.colors.GREEN}✅ 已选择: {', '.join(selected)}{self.colors.ENDC}")
                    break
                    
            except ValueError:
                print(f"{self.colors.RED}❌ 请输入有效的数字{self.colors.ENDC}")
        
        return {"models_needed": selected}
    
    def ask_budget(self) -> Optional[Dict]:
        """询问预算"""
        print(f"{self.colors.CYAN}请设置预算限制:{self.colors.ENDC}\n")
        
        budget_options = [
            ("无限制", None, "不设预算限制"),
            ("1000元/月以下", 1000, "个人/实验用途"),
            ("1000-5000元/月", 3000, "中小企业/团队"),
            ("5000-20000元/月", 10000, "企业部门级"),
            ("20000元/月以上", 50000, "企业核心业务"),
            ("自定义", "custom", "自定义预算金额")
        ]
        
        for i, (name, value, desc) in enumerate(budget_options, 1):
            print(f"  {self.colors.GREEN}{i}. {name:20} - {desc}{self.colors.ENDC}")
        
        while True:
            try:
                choice = input(f"\n{self.colors.CYAN}👉 请选择: {self.colors.ENDC}")
                
                if choice == "0":
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(budget_options):
                    if budget_options[idx][1] == "custom":
                        custom_budget = input(f"{self.colors.CYAN}请输入月预算(元): {self.colors.ENDC}")
                        try:
                            budget = float(custom_budget)
                            if budget > 0:
                                # 询问token量
                                tokens = input(f"{self.colors.CYAN}预计月token量(百万, 回车跳过): {self.colors.ENDC}")
                                monthly_tokens = int(float(tokens) * 1_000_000) if tokens else None
                                return {"budget": budget, "monthly_tokens": monthly_tokens}
                        except ValueError:
                            print(f"{self.colors.RED}❌ 请输入有效的数字{self.colors.ENDC}")
                    else:
                        budget = budget_options[idx][1]
                        return {"budget": budget}
                else:
                    print(f"{self.colors.RED}❌ 无效选择{self.colors.ENDC}")
                    
            except ValueError:
                print(f"{self.colors.RED}❌ 请输入有效的数字{self.colors.ENDC}")
    
    def ask_performance(self) -> Optional[Dict]:
        """询问性能要求"""
        print(f"{self.colors.CYAN}请设置性能要求:{self.colors.ENDC}\n")
        
        sla_options = [
            ("基础可用 (99%)", 0.99, "测试/非核心业务"),
            ("标准可用 (99.5%)", 0.995, "一般业务"),
            ("高可用 (99.9%)", 0.999, "核心业务"),
            ("极高可用 (99.95%)", 0.9995, "金融/交易系统"),
            ("自定义", "custom", "自定义SLA")
        ]
        
        print(f"{self.colors.YELLOW}SLA要求 (服务可用性):{self.colors.ENDC}")
        for i, (name, value, desc) in enumerate(sla_options, 1):
            print(f"  {self.colors.GREEN}{i}. {name:20} - {desc}{self.colors.ENDC}")
        
        sla_choice = self.get_choice(len(sla_options))
        if sla_choice == 0:
            return None
        
        if sla_options[sla_choice-1][1] == "custom":
            while True:
                try:
                    custom_sla = input(f"{self.colors.CYAN}请输入SLA要求(如0.999): {self.colors.ENDC}")
                    sla = float(custom_sla)
                    if 0.9 <= sla <= 1.0:
                        break
                    else:
                        print(f"{self.colors.RED}❌ SLA应在0.9-1.0之间{self.colors.ENDC}")
                except ValueError:
                    print(f"{self.colors.Red}❌ 请输入有效的数字{self.colors.ENDC}")
        else:
            sla = sla_options[sla_choice-1][1]
        
        # 延迟要求
        print(f"\n{self.colors.YELLOW}延迟要求:{self.colors.ENDC}")
        latency_options = [
            ("宽松 (>2000ms)", 2000, "批处理/离线任务"),
            ("一般 (1000-2000ms)", 1500, "一般交互"),
            ("快速 (500-1000ms)", 750, "实时交互"),
            ("极快 (<500ms)", 300, "高频交易/游戏"),
            ("自定义", "custom", "自定义延迟")
        ]
        
        for i, (name, value, desc) in enumerate(latency_options, 1):
            print(f"  {self.colors.GREEN}{i}. {name:20} - {desc}{self.colors.ENDC}")
        
        latency_choice = self.get_choice(len(latency_options))
        if latency_choice == 0:
            return None
        
        if latency_options[latency_choice-1][1] == "custom":
            while True:
                try:
                    custom_latency = input(f"{self.colors.CYAN}请输入延迟要求(ms): {self.colors.ENDC}")
                    latency = int(custom_latency)
                    if latency > 0:
                        break
                    else:
                        print(f"{self.colors.RED}❌ 延迟应大于0{self.colors.ENDC}")
                except ValueError:
                    print(f"{self.colors.Red}❌ 请输入有效的数字{self.colors.ENDC}")
        else:
            latency = latency_options[latency_choice-1][1]
        
        return {
            "sla_requirement": sla,
            "latency_requirement": latency
        }
    
    def ask_security(self) -> Optional[Dict]:
        """询问安全等级"""
        print(f"{self.colors.CYAN}请选择安全等级:{self.colors.ENDC}\n")
        
        security_levels = [
            ("低安全性", "low", "内部测试/非敏感数据，注重成本"),
            ("中等安全性", "medium", "一般业务数据，平衡安全与成本"),
            ("高安全性", "high", "敏感业务数据，安全优先"),
            ("最高安全性", "max", "金融/医疗等敏感数据，必须合规")
        ]
        
        for i, (name, level, desc) in enumerate(security_levels, 1):
            print(f"  {self.colors.GREEN}{i}. {name:15} - {desc}{self.colors.ENDC}")
        
        choice = self.get_choice(len(security_levels))
        if choice == 0:
            return None
        
        selected_level = security_levels[choice-1][1]
        return {"security_level": selected_level}
    
    def display_results(self, result: Dict):
        """显示分析结果"""
        self.print_header()
        print(f"{self.colors.GREEN}{self.colors.BOLD}🎯 选型分析结果{self.colors.ENDC}\n")
        
        # 基本信息
        print(f"{self.colors.CYAN}📋 分析概要:{self.colors.ENDC}")
        print(f"  分析时间: {result['timestamp']}")
        print(f"  使用场景: {result['requirements']['use_case']}")
        print(f"  安全等级: {result['requirements']['security_level']}")
        print(f"  总体风险: {result['risk_report']['overall_risk_level']}")
        print()
        
        # 推荐服务商
        print(f"{self.colors.CYAN}🏆 推荐服务商:{self.colors.ENDC}")
        providers = result.get("matched_providers", [])
        
        if providers:
            top_provider = providers[0]
            print(f"\n  {self.colors.GREEN}🥇 首选推荐: {top_provider['name']}{self.colors.ENDC}")
            print(f"     类型: {top_provider['type']}")
            print(f"     匹配分数: {top_provider.get('match_score', 0):.1f}分")
            print(f"     标签: {', '.join(top_provider.get('tags', []))}")
            print(f"     适用: {', '.join(top_provider.get('suitable_for', []))}")
            print(f"     SLA: {top_provider.get('sla', 0)*100:.2f}%")
            print(f"     风险评分: {top_provider.get('risk_score', 0)}/100")
            
            # 显示其他推荐
            if len(providers) > 1:
                print(f"\n  {self.colors.YELLOW}🏅 备选推荐:{self.colors.ENDC}")
                for i, provider in enumerate(providers[1:4], 2):
                    print(f"     {i}. {provider['name']} ({provider.get('match_score', 0):.1f}分)")
        else:
            print(f"  {self.colors.RED}⚠️ 未找到匹配的服务商{self.colors.ENDC}")
        
        # 成本分析
        cost_analysis = result.get("cost_analysis", {})
        if "analysis" in cost_analysis:
            print(f"\n{self.colors.CYAN}💰 成本分析:{self.colors.ENDC}")
            for item in cost_analysis["analysis"][:3]:
                cost = item.get("estimated_cost")
                if cost:
                    print(f"  {item['provider']}: 约¥{cost:.2f}/月")
            
            if "budget_advice" in cost_analysis:
                print(f"\n  💡 {cost_analysis['budget_advice']}")
        
        # 风险提示
        risks = result.get("risk_report", {}).get("identified_risks", [])
        if risks:
            print(f"\n{self.colors.RED}⚠️ 风险提示:{self.colors.ENDC}")
            for i, risk in enumerate(risks[:3], 1):
                severity_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.ge