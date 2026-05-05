#!/usr/bin/env python3
"""
日志系统
提供结构化的日志记录和分析功能
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any
import re

class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record):
        """格式化日志记录"""
        # 添加结构化数据
        if not hasattr(record, 'structured_data'):
            record.structured_data = {}
        
        # 格式化消息
        if isinstance(record.msg, dict):
            record.msg = json.dumps(record.msg, ensure_ascii=False)
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record):
        """转换为JSON格式"""
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # 添加结构化数据
        if hasattr(record, 'structured_data'):
            log_record.update(record.structured_data)
        
        return json.dumps(log_record, ensure_ascii=False)

class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.patterns = {
            "ERROR": r"ERROR.*",
            "WARNING": r"WARNING.*",
            "RISK": r"风险.*|危险.*|威胁.*",
            "PERFORMANCE": r"延迟.*|超时.*|性能.*|慢.*",
            "SECURITY": r"安全.*|泄露.*|攻击.*|漏洞.*"
        }
    
    def analyze_logs(self, days: int = 1) -> Dict[str, Any]:
        """分析最近N天的日志"""
        logs = self._read_recent_logs(days)
        
        if not logs:
            return {"error": f"未找到最近{days}天的日志"}
        
        analysis = {
            "total_entries": len(logs),
            "by_level": self._count_by_level(logs),
            "by_pattern": self._count_by_pattern(logs),
            "errors": self._extract_errors(logs),
            "warnings": self._extract_warnings(logs),
            "trends": self._analyze_trends(logs),
            "recommendations": []
        }
        
        # 生成建议
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _read_recent_logs(self, days: int) -> list:
        """读取最近N天的日志"""
        logs = []
        end_date = datetime.now()
        
        for i in range(days):
            date = (end_date.timestamp() - i * 86400)
            log_file = self.log_dir / f"ai_proxy_{datetime.fromtimestamp(date).strftime('%Y%m%d')}.log"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            logs.append(line.strip())
        
        return logs
    
    def _count_by_level(self, logs: list) -> Dict[str, int]:
        """按级别统计"""
        levels = ["ERROR", "WARNING", "INFO", "DEBUG"]
        counts = {level: 0 for level in levels}
        
        for log in logs:
            for level in levels:
                if f"| {level}" in log:
                    counts[level] += 1
                    break
        
        return counts
    
    def _count_by_pattern(self, logs: list) -> Dict[str, int]:
        """按模式统计"""
        counts = {key: 0 for key in self.patterns}
        
        for log in logs:
            for pattern_name, pattern in self.patterns.items():
                if re.search(pattern, log, re.IGNORECASE):
                    counts[pattern_name] += 1
        
        return counts
    
    def _extract_errors(self, logs: list) -> list:
        """提取错误信息"""
        errors = []
        for log in logs:
            if "| ERROR" in log:
                # 提取错误信息
                error_info = {
                    "message": log.split("|", 3)[-1].strip() if "|" in log else log,
                    "timestamp": log.split("|")[0].strip() if "|" in log else "Unknown"
                }
                errors.append(error_info)
        
        return errors[:20]  # 最多返回20个
    
    def _extract_warnings(self, logs: list) -> list:
        """提取警告信息"""
        warnings = []
        for log in logs:
            if "| WARNING" in log:
                warning_info = {
                    "message": log.split("|", 3)[-1].strip() if "|" in log else log,
                    "timestamp": log.split("|")[0].strip() if "|" in log else "Unknown"
                }
                warnings.append(warning_info)
        
        return warnings[:20]  # 最多返回20个
    
    def _analyze_trends(self, logs: list) -> Dict[str, Any]:
        """分析趋势"""
        if not logs:
            return {}
        
        # 按小时统计错误数
        hourly_errors = {}
        for log in logs:
            if "| ERROR" in log and "|" in log:
                timestamp = log.split("|")[0].strip()
                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    hour = dt.strftime("%Y-%m-%d %H:00")
                    hourly_errors[hour] = hourly_errors.get(hour, 0) + 1
                except:
                    pass
        
        return {
            "error_peak_hours": sorted(hourly_errors.items(), key=lambda x: x[1], reverse=True)[:5],
            "error_rate": len([l for l in logs if "| ERROR" in l]) / len(logs) if logs else 0
        }
    
    def _generate_recommendations(self, analysis: Dict) -> list:
        """生成修复建议"""
        recommendations = []
        
        # 错误率过高
        error_rate = analysis.get("trends", {}).get("error_rate", 0)
        if error_rate > 0.1:  # 错误率超过10%
            recommendations.append({
                "issue": "高错误率",
                "severity": "HIGH",
                "suggestion": "检查系统配置和依赖，错误率过高可能导致系统不稳定",
                "action": "review_configuration"
            })
        
        # 安全相关警告
        security_count = analysis.get("by_pattern", {}).get("SECURITY", 0)
        if security_count > 5:
            recommendations.append({
                "issue": "安全警告较多",
                "severity": "HIGH",
                "suggestion": "系统检测到多个安全相关警告，建议立即审查",
                "action": "security_review"
            })
        
        # 性能问题
        performance_count = analysis.get("by_pattern", {}).get("PERFORMANCE", 0)
        if performance_count > 10:
            recommendations.append({
                "issue": "性能问题",
                "severity": "MEDIUM",
                "suggestion": "系统检测到多个性能相关警告，建议优化",
                "action": "performance_optimization"
            })
        
        # 风险提示
        risk_count = analysis.get("by_pattern", {}).get("RISK", 0)
        if risk_count > 0:
            recommendations.append({
                "issue": "风险检测",
                "severity": "MEDIUM",
                "suggestion": "系统检测到风险提示，建议检查配置",
                "action": "risk_assessment"
            })
        
        return recommendations
    
    def generate_report(self, days: int = 1) -> str:
        """生成分析报告"""
        analysis = self.analyze_logs(days)
        
        report = []
        report.append("=" * 60)
        report.append("AI中转站选型系统 - 日志分析报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"分析天数: {days}")
        report.append("=" * 60)
        
        # 基本信息
        report.append(f"\n📊 基本信息:")
        report.append(f"  日志条目总数: {analysis.get('total_entries', 0)}")
        
        # 按级别统计
        report.append(f"\n📈 按级别统计:")
        for level, count in analysis.get('by_level', {}).items():
            report.append(f"  {level}: {count}")
        
        # 错误信息
        errors = analysis.get('errors', [])
        if errors:
            report.append(f"\n❌ 错误列表 (前{len(errors)}个):")
            for i, error in enumerate(errors[:5], 1):
                report.append(f"  {i}. [{error.get('timestamp')}] {error.get('message')}")
        
        # 趋势分析
        trends = analysis.get('trends', {})
        if trends.get('error_peak_hours'):
            report.append(f"\n📅 错误高峰时段:")
            for hour, count in trends['error_peak_hours'][:3]:
                report.append(f"  {hour}: {count}个错误")
        
        # 修复建议
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            report.append(f"\n🔧 修复建议:")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"  {i}. [{rec.get('severity')}] {rec.get('issue')}")
                report.append(f"     建议: {rec.get('suggestion')}")
                report.append(f"     操作: {rec.get('action')}")
        
        return "\n".join(report)

def setup_logger(name: str = "ai_proxy_advisor") -> logging.Logger:
    """设置日志记录器"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = StructuredFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（按天滚动）
    log_file = log_dir / f"ai_proxy_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 错误文件处理器
    error_file = log_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_formatter = StructuredFormatter()
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)
    
    return logger

def analyze_logs_command(days: int = 1):
    """日志分析命令"""
    analyzer = LogAnalyzer()
    report = analyzer.generate_report(days)
    print(report)
    
    # 生成修复补丁
    analysis = analyzer.analyze_logs(days)
    patches = generate_patches_from_analysis(analysis)
    
    if patches:
        print(f"\n🎯 生成 {len(patches)} 个修复补丁")
        for patch in patches:
            print(f"  - {patch.get('name')}: {patch.get('description')}")

def generate_patches_from_analysis(analysis: Dict) -> list:
    """根据分析结果生成补丁"""
    patches = []
    recommendations = analysis.get('recommendations', [])
    
    for rec in recommendations:
        if rec.get('action') == 'review_configuration':
            patches.append({
                "name": "config_fix.py",
                "description": "修复配置问题",
                "priority": "HIGH",
                "code": '''
def fix_configuration_issues():
    """修复配置问题"""
    import yaml
    from pathlib import Path
    
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 添加默认配置
        if 'logging' not in config:
            config['logging'] = {
                'level': 'INFO',
                'rotation': 'daily',
                'retention': 30
            }
        
        if 'security' not in config:
            config['security'] = {
                'encryption': True,
                'timeout': 30,
                'retry_attempts': 3
            }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return True
    return False
'''
            })
    
    return patches