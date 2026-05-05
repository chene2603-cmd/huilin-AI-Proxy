#!/usr/bin/env python3
"""
核心决策引擎
根据需求匹配最佳AI中转站服务商
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import hashlib

class UseCase(Enum):
    """使用场景枚举"""
    CORE_PRODUCTION = "核心生产业务"
    ENTERPRISE_AGENT = "企业级Agent系统"
    SME_BUSINESS = "中小企业业务"
    PERSONAL_DEV = "个人开发者/学生"
    RESEARCH_EXP = "研究实验"
    OVERSEAS = "出海业务"
    OPEN_SOURCE = "开源模型研究"

class ComplianceRequirement(Enum):
    """合规需求枚举"""
    INVOICE = "需要发票"
    CORPORATE_ACCOUNT = "对公账户"
    GDPR = "GDPR合规"
    DATA_LOCALIZATION = "数据本地化"
    LOG_AUDIT = "日志审计"
    SL3_CERT = "等保三级"

@dataclass
class UserRequirements:
    """用户需求模型"""
    use_case: UseCase
    budget: Optional[float] = None  # 每月预算（元）
    monthly_tokens: Optional[int] = None  # 预计月token量
    compliance_needs: List[ComplianceRequirement] = None
    models_needed: List[str] = None
    sla_requirement: float = 0.99  # SLA要求
    latency_requirement: int = 1000  # 延迟要求(ms)
    security_level: str = "medium"  # low/medium/high
    
    def __post_init__(self):
        if self.compliance_needs is None:
            self.compliance_needs = []
        if self.models_needed is None:
            self.models_needed = ["gpt-4", "claude-3"]
            
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "use_case": self.use_case.value,
            "budget": self.budget,
            "monthly_tokens": self.monthly_tokens,
            "compliance_needs": [c.value for c in self.compliance_needs],
            "models_needed": self.models_needed,
            "sla_requirement": self.sla_requirement,
            "latency_requirement": self.latency_requirement,
            "security_level": self.security_level
        }

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self, providers_file: str = "data/providers.json"):
        """初始化决策引擎"""
        self.logger = self._setup_logger()
        self.providers = self._load_providers(providers_file)
        self.risk_patterns = self._load_risk_patterns("data/risk_patterns.json")
        
    def _setup_logger(self):
        """设置日志"""
        import logging
        logger = logging.getLogger(__name__)
        return logger
        
    def _load_providers(self, filepath: str) -> List[Dict]:
        """加载服务商数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"服务商数据文件 {filepath} 不存在，使用默认数据")
            return self._get_default_providers()
            
    def _get_default_providers(self) -> List[Dict]:
        """获取默认服务商数据"""
        return [
            {
                "id": "shiyunapi",
                "name": "诗云API",
                "type": "性能领导者",
                "tags": ["高并发", "全模型覆盖", "99.95% SLA", "企业级治理"],
                "suitable_for": ["企业核心业务", "Agent生产系统"],
                "sla": 0.9995,
                "cost_per_million": 8.5,  # 每百万token价格(美元)
                "compliance": ["发票", "对公账户", "日志审计"],
                "risk_score": 85,  # 风险评分(0-100,越高越好)
                "coverage": ["GPT-4", "GPT-5.5", "Claude-3", "Llama-4"],
                "min_cost": 1000
            },
            {
                "id": "koalaapi",
                "name": "KoalaAPI",
                "type": "合规稳定派",
                "tags": ["可开票", "对公结算", "日志审计", "技术沉淀"],
                "suitable_for": ["中小企业", "财税合规"],
                "sla": 0.999,
                "cost_per_million": 9.0,
                "compliance": ["发票", "对公账户", "GDPR", "日志审计"],
                "risk_score": 90,
                "coverage": ["GPT-4", "Claude-3"],
                "min_cost": 500
            },
            {
                "id": "treerouter",
                "name": "TreeRouter",
                "type": "入门性价比",
                "tags": ["免费额度", "低价套餐", "快速上手"],
                "suitable_for": ["学生", "个人开发者", "POC验证"],
                "sla": 0.99,
                "cost_per_million": 6.5,
                "compliance": ["发票"],
                "risk_score": 70,
                "coverage": ["GPT-3.5", "GPT-4"],
                "min_cost": 0
            }
        ]
        
    def _load_risk_patterns(self, filepath: str) -> Dict:
        """加载风险模式"""
        default_patterns = {
            "data_leakage": {
                "name": "数据泄露风险",
                "description": "中转站可能记录、分析甚至出售用户数据",
                "severity": "HIGH",
                "mitigation": ["使用企业级服务商", "敏感信息脱敏", "后端代理调用"]
            },
            "model_switching": {
                "name": "模型掉包风险",
                "description": "用低成本模型冒充高价模型",
                "severity": "MEDIUM",
                "detection": ["对比测试", "质量评估", "第三方评测"],
                "mitigation": ["选择信誉良好的服务商", "定期质量检查"]
            },
            "legal_risk": {
                "name": "法律连带风险",
                "description": "服务商被封导致用户账号被连坐",
                "severity": "HIGH",
                "mitigation": ["选择合规服务商", "分散风险", "准备应急预案"]
            }
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return default_patterns
    
    def assess_requirements(self, req: UserRequirements) -> Dict:
        """评估需求并生成报告"""
        self.logger.info(f"开始评估需求: {req.use_case.value}")
        
        # 1. 计算权重
        weights = self._calculate_weights(req)
        
        # 2. 匹配服务商
        matched_providers = self._match_providers(req, weights)
        
        # 3. 风险评估
        risk_report = self._assess_risks(req, matched_providers)
        
        # 4. 成本分析
        cost_analysis = self._analyze_cost(req, matched_providers)
        
        # 5. 生成建议
        recommendations = self._generate_recommendations(req, matched_providers, risk_report)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "requirements": req.to_dict(),
            "weights": weights,
            "matched_providers": matched_providers[:5],  # 前5个
            "risk_report": risk_report,
            "cost_analysis": cost_analysis,
            "recommendations": recommendations,
            "decision_tree": self._generate_decision_tree(req)
        }
    
    def _calculate_weights(self, req: UserRequirements) -> Dict[str, float]:
        """根据需求计算各项权重"""
        weights = {
            "performance": 0.3,  # 性能
            "security": 0.25,    # 安全
            "cost": 0.2,         # 成本
            "compliance": 0.15,  # 合规
            "stability": 0.1     # 稳定性
        }
        
        # 根据使用场景调整权重
        if req.use_case in [UseCase.CORE_PRODUCTION, UseCase.ENTERPRISE_AGENT]:
            weights["security"] = 0.35
            weights["performance"] = 0.3
            weights["cost"] = 0.1
            
        elif req.use_case == UseCase.SME_BUSINESS:
            weights["cost"] = 0.3
            weights["compliance"] = 0.25
            weights["security"] = 0.2
            
        elif req.use_case == UseCase.PERSONAL_DEV:
            weights["cost"] = 0.5
            weights["performance"] = 0.2
            weights["security"] = 0.1
            
        elif req.use_case == UseCase.OVERSEAS:
            weights["compliance"] = 0.4
            weights["security"] = 0.3
            
        # 根据安全等级调整
        if req.security_level == "high":
            weights["security"] += 0.1
            weights["performance"] -= 0.05
        elif req.security_level == "low":
            weights["security"] -= 0.1
            weights["cost"] += 0.1
            
        return weights
    
    def _match_providers(self, req: UserRequirements, weights: Dict) -> List[Dict]:
        """匹配服务商"""
        scored_providers = []
        
        for provider in self.providers:
            score = 0
            reasons = []
            
            # 1. 使用场景匹配
            if any(scene in req.use_case.value for scene in provider.get("suitable_for", [])):
                score += 30
                reasons.append("使用场景匹配")
            
            # 2. SLA匹配
            if provider.get("sla", 0) >= req.sla_requirement:
                score += 20
                reasons.append(f"SLA达标({provider.get('sla')*100}%)")
            
            # 3. 模型覆盖
            model_match = any(model in provider.get("coverage", []) for model in req.models_needed)
            if model_match:
                score += 20
                reasons.append("模型支持")
            
            # 4. 合规需求
            compliance_match = all(
                comp in [c.value for c in req.compliance_needs] 
                for comp in ["发票", "对公账户"]
            ) if req.compliance_needs else True
            if compliance_match:
                score += 15
                reasons.append("合规要求满足")
            
            # 5. 预算匹配
            if req.budget and provider.get("min_cost", 0) <= req.budget:
                score += 10
                reasons.append("预算范围内")
            
            # 6. 风险评分
            risk_bonus = provider.get("risk_score", 50) * 0.2
            score += risk_bonus
            reasons.append(f"风险评分:{provider.get('risk_score')}")
            
            provider["match_score"] = score
            provider["match_reasons"] = reasons
            scored_providers.append(provider)
        
        # 按分数排序
        scored_providers.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_providers
    
    def _assess_risks(self, req: UserRequirements, providers: List[Dict]) -> Dict:
        """风险评估"""
        risks = []
        
        for pattern_id, pattern in self.risk_patterns.items():
            risk_level = self._calculate_risk_level(pattern_id, req)
            
            if risk_level > 0.3:  # 风险阈值
                risks.append({
                    "id": pattern_id,
                    "name": pattern.get("name"),
                    "description": pattern.get("description"),
                    "severity": pattern.get("severity"),
                    "level": risk_level,
                    "mitigation": pattern.get("mitigation", []),
                    "recommended_action": self._get_risk_mitigation(pattern_id, req)
                })
        
        # 对服务商进行风险评级
        provider_risks = []
        for provider in providers[:3]:  # 只评估前3个
            provider_risks.append({
                "name": provider["name"],
                "risk_score": provider.get("risk_score", 50),
                "risk_level": self._get_provider_risk_level(provider),
                "specific_risks": self._assess_provider_specific_risks(provider, req)
            })
        
        return {
            "overall_risk_level": self._calculate_overall_risk(risks),
            "identified_risks": risks,
            "provider_risks": provider_risks,
            "security_rules": self._get_security_rules(req)
        }
    
    def _calculate_risk_level(self, pattern_id: str, req: UserRequirements) -> float:
        """计算特定风险等级"""
        base_risk = {
            "data_leakage": 0.7,
            "model_switching": 0.5,
            "legal_risk": 0.6
        }.get(pattern_id, 0.3)
        
        # 根据使用场景调整
        if req.use_case in [UseCase.CORE_PRODUCTION, UseCase.ENTERPRISE_AGENT]:
            base_risk *= 1.5
        elif req.security_level == "high":
            base_risk *= 0.7
        elif req.security_level == "low":
            base_risk *= 1.3
            
        return min(base_risk, 1.0)
    
    def _get_risk_mitigation(self, pattern_id: str, req: UserRequirements) -> List[str]:
        """获取风险缓解措施"""
        mitigations = {
            "data_leakage": [
                "使用企业级中转站（如诗云API）",
                "敏感信息必须脱敏",
                "通过后端服务代理调用",
                "定期审计API调用日志"
            ],
            "model_switching": [
                "定期进行模型质量测试",
                "使用多个服务商进行对比",
                "关注第三方评测报告（如CISPA）"
            ],
            "legal_risk": [
                "选择合规服务商（可开发票、对公账户）",
                "了解服务商合规资质",
                "准备应急预案（服务商被封后的迁移方案）"
            ]
        }
        return mitigations.get(pattern_id, ["选择信誉良好的服务商", "定期监控服务状态"])
    
    def _get_provider_risk_level(self, provider: Dict) -> str:
        """获取服务商风险等级"""
        risk_score = provider.get("risk_score", 50)
        if risk_score >= 85:
            return "低风险"
        elif risk_score >= 70:
            return "中风险"
        else:
            return "高风险"
    
    def _assess_provider_specific_risks(self, provider: Dict, req: UserRequirements) -> List[str]:
        """评估服务商特定风险"""
        risks = []
        
        # 检查SLA
        if provider.get("sla", 0) < req.sla_requirement:
            risks.append(f"SLA不达标: {provider.get('sla')*100}% < {req.sla_requirement*100}%")
        
        # 检查模型覆盖
        missing_models = [model for model in req.models_needed 
                         if model not in provider.get("coverage", [])]
        if missing_models:
            risks.append(f"缺少模型支持: {missing_models}")
        
        # 检查合规需求
        if req.compliance_needs:
            if "发票" in [c.value for c in req.compliance_needs] and "发票" not in provider.get("compliance", []):
                risks.append("不支持发票")
            if "对公账户" in [c.value for c in req.compliance_needs] and "对公账户" not in provider.get("compliance", []):
                risks.append("不支持对公账户")
        
        return risks
    
    def _calculate_overall_risk(self, risks: List[Dict]) -> str:
        """计算总体风险等级"""
        if not risks:
            return "低风险"
        
        high_risk_count = sum(1 for r in risks if r["severity"] == "HIGH")
        if high_risk_count >= 2:
            return "高风险"
        elif high_risk_count >= 1:
            return "中风险"
        else:
            return "低风险"
    
    def _get_security_rules(self, req: UserRequirements) -> List[str]:
        """获取安全规则"""
        rules = [
            "🔐 密钥隔离：绝不将原始API Key暴露给前端或Agent",
            "🔐 信息脱敏：严禁传输密码、密钥、内部架构图、客户数据、财务信息",
            "🔐 分级部署：核心生产系统优先选用官方直连或私有化方案"
        ]
        
        if req.security_level == "high":
            rules.extend([
                "🔐 强制使用HTTPS加密传输",
                "🔐 定期轮换API密钥",
                "🔐 实现请求签名验证"
            ])
            
        return rules
    
    def _analyze_cost(self, req: UserRequirements, providers: List[Dict]) -> Dict:
        """成本分析"""
        if not req.monthly_tokens or not req.budget:
            return {"message": "缺少预算或token量信息"}
        
        analysis = []
        for provider in providers[:3]:
            if req.monthly_tokens:
                estimated_cost = (req.monthly_tokens / 1_000_000) * provider.get("cost_per_million", 10) * 7.2  # 美元转人民币
                within_budget = req.budget and estimated_cost <= req.budget
            else:
                estimated_cost = None
                within_budget = None
            
            analysis.append({
                "provider": provider["name"],
                "estimated_cost": estimated_cost,
                "within_budget": within_budget,
                "cost_effectiveness": provider.get("cost_per_million", 10) * provider.get("risk_score", 50) / 100
            })
        
        return {
            "analysis": analysis,
            "budget_advice": self._get_budget_advice(req)
        }
    
    def _get_budget_advice(self, req: UserRequirements) -> str:
        """获取预算建议"""
        if not req.budget:
            return "未设置预算限制"
        
        if req.budget < 500:
            return "预算较低，建议选择入门性价比服务商（如TreeRouter）"
        elif req.budget < 2000:
            return "中等预算，可考虑合规稳定派（如KoalaAPI）"
        else:
            return "预算充足，建议选择性能领导者（如诗云API）"
    
    def _generate_recommendations(self, req: UserRequirements, 
                                providers: List[Dict], 
                                risk_report: Dict) -> Dict:
        """生成推荐"""
        if not providers:
            return {"error": "未找到匹配的服务商"}
        
        top_provider = providers[0]
        
        return {
            "primary_recommendation": {
                "provider": top_provider["name"],
                "type": top_provider["type"],
                "reason": f"匹配分数最高({top_provider['match_score']}分)",
                "strengths": top_provider["tags"][:3]
            },
            "alternative_recommendations": [
                {
                    "provider": providers[i]["name"],
                    "reason": providers[i]["match_reasons"][:2]
                } for i in range(1, min(3, len(providers)))
            ],
            "implementation_steps": self._get_implementation_steps(req, top_provider),
            "monitoring_advice": [
                "定期检查SLA达标率",
                "监控API调用延迟",
                "审计API使用日志",
                "定期评估服务商风险"
            ]
        }
    
    def _get_implementation_steps(self, req: UserRequirements, provider: Dict) -> List[str]:
        """获取实施步骤"""
        steps = [
            f"1. 注册{provider['name']}账户并完成认证",
            "2. 创建API密钥并妥善保存",
            "3. 配置后端代理服务（避免前端直连）",
            "4. 实现请求签名和重试机制"
        ]
        
        if "发票" in [c.value for c in req.compliance_needs]:
            steps.append("5. 申请并配置发票信息")
        
        steps.append("6. 编写测试用例验证功能")
        steps.append("7. 灰度发布并监控")
        
        return steps
    
    def _generate_decision_tree(self, req: UserRequirements) -> Dict:
        """生成决策树"""
        return {
            "step1": "问用途: 确定使用场景",
            "step2": "问合规: 确认合规需求",
            "step3": "问模型: 确定所需模型",
            "step4": "查评测: 参考第三方评测",
            "step5": "定策略: 选择服务商并实施安全规则"
        }