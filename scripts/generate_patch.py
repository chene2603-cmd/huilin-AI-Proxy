#!/usr/bin/env python3
"""
补丁生成脚本
根据需求自动生成补丁代码
"""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import inspect
import re

class PatchGenerator:
    """补丁生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """加载补丁模板"""
        return {
            "security_fix": self._get_security_fix_template(),
            "performance_optimization": self._get_performance_template(),
            "bug_fix": self._get_bug_fix_template(),
            "feature_add": self._get_feature_template(),
            "compliance_update": self._get_compliance_template(),
            "risk_mitigation": self._get_risk_mitigation_template()
        }
    
    def _get_security_fix_template(self) -> str:
        """获取安全修复模板"""
        return '''def patched_function(*args, **kwargs):
    """
    安全补丁函数
    添加安全检查、输入验证、加密等
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 1. 输入验证
    original_args = args
    original_kwargs = kwargs
    
    # 检查敏感信息
    sensitive_patterns = [
        r'password[=:]\s*[\'"]?[^\'"\\s]+[\'"]?',
        r'apikey[=:]\s*[\'"]?[^\'"\\s]+[\'"]?',
        r'token[=:]\s*[\'"]?[^\'"\\s]+[\'"]?',
        r'secret[=:]\s*[\'"]?[^\'"\\s]+[\'"]?'
    ]
    
    args_str = str(args) + str(kwargs)
    for pattern in sensitive_patterns:
        if re.search(pattern, args_str, re.IGNORECASE):
            logger.warning("⚠️ 检测到敏感信息传输")
            # 可以在这里添加脱敏逻辑
            # 或者抛出异常阻止调用
    
    # 2. 添加请求签名验证
    if 'signature' not in kwargs:
        logger.warning("缺少请求签名")
        # 可以在这里添加签名验证逻辑
    
    # 3. 调用原函数
    try:
        result = original_function(*original_args, **original_kwargs)
        
        # 4. 输出验证
        if isinstance(result, dict) and 'error' in result:
            logger.error(f"API调用错误: {{result['error']}}")
        
        return result
        
    except Exception as e:
        logger.error(f"安全补丁捕获异常: {{e}}")
        raise
    
    finally:
        # 5. 清理敏感信息
        del args_str
'''

    def _get_performance_template(self) -> str:
        """获取性能优化模板"""
        return '''def patched_function(*args, **kwargs):
    """
    性能优化补丁
    添加缓存、批量处理、连接池等
    """
    import time
    import hashlib
    import logging
    from functools import lru_cache
    
    logger = logging.getLogger(__name__)
    start_time = time.time()
    
    # 1. 参数缓存键
    cache_key = None
    if len(args) + len(kwargs) < 10:  # 参数不多时使用缓存
        cache_key = hashlib.md5(
            (str(args) + str(sorted(kwargs.items()))).encode()
        ).hexdigest()
    
    # 2. 检查缓存
    if cache_key and hasattr(patched_function, '_cache'):
        if cache_key in patched_function._cache:
            logger.debug(f"缓存命中: {{cache_key[:8]}}")
            return patched_function._cache[cache_key]
    
    # 3. 添加超时控制
    import signal
    
    class TimeoutException(Exception):
        pass
    
    def timeout_handler(signum, frame):
        raise TimeoutException("函数执行超时")
    
    # 设置超时（默认30秒）
    timeout = kwargs.pop('timeout', 30)
    original_signal = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        # 4. 调用原函数
        result = original_function(*args, **kwargs)
        
        # 5. 更新缓存
        if cache_key:
            if not hasattr(patched_function, '_cache'):
                patched_function._cache = {}
            patched_function._cache[cache_key] = result
        
        return result
        
    except TimeoutException as e:
        logger.error(f"函数执行超时: {{timeout}}秒")
        raise
        
    finally:
        # 6. 恢复信号
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_signal)
        
        # 7. 记录性能指标
        elapsed = time.time() - start_time
        if elapsed > 1.0:  # 超过1秒记录警告
            logger.warning(f"函数执行时间过长: {{elapsed:.2f}}秒")
        else:
            logger.debug(f"函数执行时间: {{elapsed:.3f}}秒")
'''

    def _get_bug_fix_template(self) -> str:
        """获取BUG修复模板"""
        return '''def patched_function(*args, **kwargs):
    """
    BUG修复补丁
    修复已知问题、边界条件处理
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 1. 参数验证和修复
    fixed_args = []
    for arg in args:
        if arg is None:
            logger.warning("参数为None，使用默认值")
            fixed_args.append(None)  # 或适当的默认值
        else:
            fixed_args.append(arg)
    
    fixed_kwargs = {}
    for key, value in kwargs.items():
        if value is None:
            logger.warning(f"参数{{key}}为None，使用默认值")
            fixed_kwargs[key] = None  # 或适当的默认值
        else:
            fixed_kwargs[key] = value
    
    # 2. 特定BUG修复
    # 修复已知的边界条件
    if len(fixed_args) > 0 and isinstance(fixed_args[0], str):
        # 修复字符串编码问题
        fixed_args[0] = fixed_args[0].encode('utf-8', errors='ignore').decode('utf-8')
    
    # 3. 调用原函数
    try:
        result = original_function(*fixed_args, **fixed_kwargs)
        
        # 4. 结果验证和修复
        if result is None:
            logger.warning("函数返回None，返回默认值")
            return {}  # 返回适当的默认值
        
        # 修复结果中的None值
        if isinstance(result, dict):
            for key, value in list(result.items()):
                if value is None:
                    logger.warning(f"结果中{{key}}为None")
                    result[key] = ""
        
        return result
        
    except KeyError as e:
        logger.error(f"键错误: {{e}}，尝试修复")
        # 尝试使用默认值
        return {{"error": f"键{{e}}不存在", "data": {{}}}}
        
    except ValueError as e:
        logger.error(f"值错误: {{e}}，尝试修复")
        # 尝试使用默认值
        return {{"error": f"值错误: {{e}}", "data": {{}}}}
        
    except Exception as e:
        logger.error(f"未预期的错误: {{e}}")
        raise
'''

    def _get_feature_template(self) -> str:
        """获取功能添加模板"""
        return '''def patched_function(*args, **kwargs):
    """
    功能增强补丁
    添加新功能、扩展接口
    """
    import logging
    import json
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    # 1. 新增功能: 添加调用追踪
    trace_id = kwargs.pop('trace_id', None)
    if not trace_id:
        import uuid
        trace_id = str(uuid.uuid4())[:8]
    
    logger.info(f"调用追踪 [{{trace_id}}]: {{original_function.__name__}}")
    
    # 2. 新增功能: 添加请求/响应日志
    if kwargs.get('enable_logging', True):
        log_data = {{
            "trace_id": trace_id,
            "function": original_function.__name__,
            "timestamp": datetime.now().isoformat(),
            "args": str(args)[:200],  # 限制长度
            "kwargs_keys": list(kwargs.keys())
        }}
        logger.debug(f"请求数据: {{json.dumps(log_data, ensure_ascii=False)}}")
    
    # 3. 新增功能: 添加重试机制
    max_retries = kwargs.pop('max_retries', 3)
    retry_delay = kwargs.pop('retry_delay', 1)
    
    for attempt in range(max_retries):
        try:
            result = original_function(*args, **kwargs)
            
            # 4. 新增功能: 添加响应日志
            if kwargs.get('enable_logging', True):
                response_log = {{
                    "trace_id": trace_id,
                    "success": True,
                    "attempt": attempt + 1,
                    "timestamp": datetime.now().isoformat()
                }}
                if isinstance(result, dict):
                    response_log["has_data"] = bool(result)
                logger.debug(f"响应数据: {{json.dumps(response_log, ensure_ascii=False)}}")
            
            return result
            
        except Exception as e:
            logger.warning(f"尝试{{attempt+1}}失败: {{e}}")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (2 ** attempt))  # 指数退避
            else:
                logger.error(f"所有{{max_retries}}次尝试都失败")
                raise
    
    # 5. 新增功能: 返回扩展结果
    # 可以在结果中添加额外信息
    if isinstance(result, dict):
        result["_metadata"] = {{
            "trace_id": trace_id,
            "processed_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }}
    
    return result
'''

    def _get_compliance_template(self) -> str:
        """获取合规性更新模板"""
        return '''def patched_function(*args, **kwargs):
    """
    合规性补丁
    添加GDPR、数据本地化、审计日志等合规功能
    """
    import logging
    import hashlib
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    # 1. GDPR合规: 数据脱敏
    def gdpr_mask_data(data):
        """GDPR数据脱敏"""
        if isinstance(data, str) and len(data) > 0:
            if '@' in data:  # 邮箱
                local, domain = data.split('@', 1)
                if len(local) > 2:
                    masked = local[0] + '*' * (len(local)-2) + local[-1]
                else:
                    masked = '*' * len(local)
                return f"{{masked}}@{{domain}}"
            elif len(data) > 4:  # 其他敏感信息
                return data[0] + '*' * (len(data)-2) + data[-1]
        return data
    
    # 2. 数据本地化检查
    data_localization_required = kwargs.pop('data_localization', False)
    if data_localization_required:
        # 检查是否包含跨境数据传输
        logger.info("数据本地化检查启用")
        # 可以在这里添加数据位置验证逻辑
    
    # 3. 审计日志
    audit_data = {{
        "timestamp": datetime.now().isoformat(),
        "function": original_function.__name__,
        "user_id": kwargs.get('user_id', 'anonymous'),
        "action": "api_call"
    }}
    
    # 记录审计日志
    audit_logger = logging.getLogger('audit')
    audit_logger.info(json.dumps(audit_data, ensure_ascii=False))
    
    # 4. 调用原函数
    try:
        # 处理参数中的敏感信息
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(gdpr_mask_data(arg))
            else:
                safe_args.append(arg)
        
        safe_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str) and key.lower() in ['email', 'phone', 'name', 'idcard']:
                safe_kwargs[key] = gdpr_mask_data(value)
            else:
                safe_kwargs[key] = value
        
        result = original_function(*safe_args, **safe_kwargs)
        
        # 5. 响应数据合规检查
        if isinstance(result, dict):
            # 检查是否包含敏感信息
            sensitive_fields = ['password', 'token', 'secret', 'credit_card']
            for field in sensitive_fields:
                if field in result:
                    logger.warning(f"响应中包含敏感字段: {{field}}")
                    result[field] = '***MASKED***'
        
        return result
        
    except Exception as e:
        # 记录错误到审计日志
        audit_data["error"] = str(e)
        audit_data["status"] = "failed"
        audit_logger.error(json.dumps(audit_data, ensure_ascii=False))
        raise
'''

    def _get_risk_mitigation_template(self) -> str:
        """获取风险缓解模板"""
        return '''def patched_function(*args, **kwargs):
    """
    风险缓解补丁
    针对AI中转站特定风险添加防护措施
    """
    import logging
    import re
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    # 1. 风险1: 数据泄露防护
    def detect_sensitive_data(data_str):
        """检测敏感数据"""
        patterns = {
            # AWS密钥
            'aws_key': r'AKIA[0-9A-Z]{16}',
            # 数据库连接字符串
            'db_connection': r'(mysql|postgresql|mongodb)://[^\\s]+',
            # 内部IP地址
            'internal_ip': r'(10\\.|172\\.(1[6-9]|2[0-9]|3[0-1])|192\\.168)\\.[0-9]+\\.[0-9]+',
            # API密钥模式
            'api_key': r'sk-[a-zA-Z0-9]{48}',
        }
        
        detected = []
        for data_type, pattern in patterns.items():
            if re.search(pattern, data_str, re.IGNORECASE):
                detected.append(data_type)
        
        return detected
    
    # 2. 检查输入中的敏感信息
    all_input = str(args) + str(kwargs)
    sensitive_types = detect_sensitive_data(all_input)
    
    if sensitive_types:
        logger.error(f"🚨 检测到敏感信息: {{sensitive_types}}")
        
        # 风险缓解措施
        mitigation = kwargs.get('risk_mitigation', 'block')
        
        if mitigation == 'block':
            raise ValueError(f"安全策略阻止: 包含敏感信息 {{sensitive_types}}")
        elif mitigation == 'mask':
            # 脱敏处理
            for data_type in sensitive_types:
                if data_type == 'aws_key':
                    all_input = re.sub(r'AKIA[0-9A-Z]{16}', 'AKIA************', all_input)
                elif data_type == 'api_key':
                    all_input = re.sub(r'sk-[a-zA-Z0-9]{48}', 'sk-********************************', all_input)
            logger.warning("敏感信息已脱敏")
        elif mitigation == 'log_only':
            logger.warning("仅记录敏感信息，不阻断")
    
    # 3. 风险2: 模型掉包检测
    enable_model_validation = kwargs.pop('validate_model', False)
    
    if enable_model_validation:
        def validate_model_response(response):
            """验证模型响应质量"""
            if isinstance(response, dict) and 'choices' in response:
                choices = response['choices']
                if choices and len(choices) > 0:
                    # 简单质量检查：响应长度
                    text = choices[0].get('text', '')
                    if len(text) < 10:
                        logger.warning("模型响应过短，可能被掉包")
                        return False
            return True
        
        # 保存验证函数供后续使用
        kwargs['_model_validator'] = validate_model_response
    
    # 4. 风险3: 请求频率限制
    if not hasattr(patched_function, '_rate_limiter'):
        from collections import deque
        import time
        patched_function._rate_limiter = {
            'requests': deque(maxlen=100),
            'limit': 60,  # 每分钟60次
            'window': 60  # 60秒窗口
        }
    
    limiter = patched_function._rate_limiter
    current_time = time.time()
    
    # 清理旧请求
    while limiter['requests'] and current_time - limiter['requests'][0] > limiter['window']:
        limiter['requests'].popleft()
    
    # 检查频率
    if len(limiter['requests']) >= limiter['limit']:
        logger.error("🚨 频率限制触发")
        raise Exception(f"频率限制: 每分钟{{limiter['limit']}}次")
    
    # 记录本次请求
    limiter['requests'].append(current_time)
    
    # 5. 调用原函数
    try:
        result = original_function(*args, **kwargs)
        
        # 6. 响应风险检查
        if enable_model_validation and '_model_validator' in kwargs:
            if not kwargs['_model_validator'](result):
                logger.error("模型响应验证失败")
                result['_warning'] = '模型响应质量可疑'
        
        return result
        
    except Exception as e:
        # 风险事件记录
        risk_event = {
            "timestamp": datetime.now().isoformat(),
            "function": original_function.__name__,
            "risk_type": "api_call_failed",
            "error": str(e),
            "sensitive_detected": sensitive_types
        }
        
        risk_logger = logging.getLogger('risk')
        risk_logger.error(json.dumps(risk_event, ensure_ascii=False))
        
        raise
'''

    def generate_from_requirement(self, 
                                requirement: Dict[str, Any]) -> Optional[str]:
        """根据需求生成补丁"""
        patch_type = requirement.get("type", "bug_fix")
        target = requirement.get("target", {}