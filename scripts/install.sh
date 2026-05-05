#!/bin/bash
# AI中转站选型系统 - 安装脚本
# 使用方法: ./scripts/install.sh

set -e  # 遇到错误退出

echo "🚀 AI中转站选型系统安装开始..."

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]]; then
    echo "❌ 需要Python 3.8或更高版本，当前版本: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python版本: $PYTHON_VERSION"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📚 安装依赖包..."
pip install -r requirements.txt

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p logs
mkdir -p data
mkdir -p patches
mkdir -p tests

# 初始化配置文件
if [ ! -f "config.yaml" ]; then
    echo "⚙️ 创建配置文件..."
    cat > config.yaml << 'EOF'
# AI中转站选型系统配置
system:
  name: "AI中转站选型辅助与风险审计系统"
  version: "1.0.0"
  debug: false

logging:
  level: "INFO"
  format: "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
  file: "logs/ai_proxy_%Y%m%d.log"
  max_size: 10485760  # 10MB
  backup_count: 5

security:
  encryption: true
  timeout: 30
  retry_attempts: 3
  rate_limit: 100  # 每分钟最大请求数

providers:
  data_file: "data/providers.json"
  update_frequency: 86400  # 24小时
  default_risk_threshold: 70

analysis:
  enable_auto_analysis: true
  analysis_interval: 3600  # 1小时
  keep_reports_days: 30
EOF
fi

# 初始化数据文件
if [ ! -f "data/providers.json" ]; then
    echo "📊 创建服务商数据文件..."
    python3 -c "
import json
data = [
    {
        'id': 'shiyunapi',
        'name': '诗云API',
        'type': '性能领导者',
        'tags': ['高并发', '全模型覆盖', '99.95% SLA', '企业级治理'],
        'suitable_for': ['企业核心业务', 'Agent生产系统'],
        'sla': 0.9995,
        'cost_per_million': 8.5,
        'compliance': ['发票', '对公账户', '日志审计'],
        'risk_score': 85,
        'coverage': ['GPT-4', 'GPT-5.5', 'Claude-3', 'Llama-4'],
        'min_cost': 1000
    }
]
with open('data/providers.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
"
fi

if [ ! -f "data/risk_patterns.json" ]; then
    echo "⚠️ 创建风险模式文件..."
    python3 -c "
import json
data = {
    'data_leakage': {
        'name': '数据泄露风险',
        'description': '中转站可能记录、分析甚至出售用户数据',
        'severity': 'HIGH',
        'mitigation': ['使用企业级服务商', '敏感信息脱敏', '后端代理调用']
    }
}
with open('data/risk_patterns.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
"
fi

# 设置文件权限
echo "🔐 设置文件权限..."
chmod +x scripts/*.sh
chmod +x main.py

# 运行自检
echo "🔍 运行系统自检..."
python3 -c "
from src.core.self_check import SystemSelfCheck
checker = SystemSelfCheck()
if checker.run_checks():
    print('✅ 系统自检通过！')
else:
    print('❌ 系统自检失败，请检查以上错误')
    exit(1)
"

echo ""
echo "✨ 安装完成！"
echo ""
echo "使用方式:"
echo "1. 启动系统: ./scripts/start.sh"
echo "2. 查看日志: tail -f logs/ai_proxy_$(date +%Y%m%d).log"
echo "3. 分析日志: python3 -c 'from src.utils.logger import analyze_logs_command; analyze_logs_command(1)'"
echo ""