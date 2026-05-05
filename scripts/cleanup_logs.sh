#!/bin/bash
# AI中转站选型系统 - 日志清理脚本
# 使用方法: ./scripts/cleanup_logs.sh [保留天数]

set -e

KEEP_DAYS=${1:-30}
LOG_DIR="logs"
BACKUP_DIR="logs/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🧹 开始清理日志文件..."
echo "保留天数: $KEEP_DAYS 天"
echo "当前时间: $(date)"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份即将清理的日志
echo "📦 备份旧日志..."
find "$LOG_DIR" -name "*.log" -mtime +$KEEP_DAYS | while read file; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        backup_file="$BACKUP_DIR/${filename%.log}_${TIMESTAMP}.log.gz"
        echo "  备份: $file -> $backup_file"
        gzip -c "$file" > "$backup_file"
    fi
done

# 清理旧日志
echo "🗑️  清理过期日志..."
OLD_COUNT=$(find "$LOG_DIR" -name "*.log" -mtime +$KEEP_DAYS | wc -l)
if [ $OLD_COUNT -gt 0 ]; then
    echo "  找到 $OLD_COUNT 个过期日志文件"
    find "$LOG_DIR" -name "*.log" -mtime +$KEEP_DAYS -delete
    echo "  ✅ 已清理"
else
    echo "  ℹ️  没有过期日志"
fi

# 清理空文件
echo "🧽 清理空文件..."
find "$LOG_DIR" -type f -name "*.log" -size 0 -delete

# 清理旧备份
echo "🗑️  清理旧备份(超过90天)..."
BACKUP_OLD_COUNT=$(find "$BACKUP_DIR" -name "*.log.gz" -mtime +90 | wc -l)
if [ $BACKUP_OLD_COUNT -gt 0 ]; then
    echo "  找到 $BACKUP_OLD_COUNT 个旧备份文件"
    find "$BACKUP_DIR" -name "*.log.gz" -mtime +90 -delete
    echo "  ✅ 已清理旧备份"
fi

# 统计信息
echo ""
echo "📊 清理完成统计:"
echo "=================="
TOTAL_LOGS=$(find "$LOG_DIR" -name "*.log" | wc -l)
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "*.log.gz" | wc -l)
TOTAL_SIZE=$(find "$LOG_DIR" -name "*.log" -exec ls -l {} \; | awk '{sum += $5} END {print sum}')
BACKUP_SIZE=$(find "$BACKUP_DIR" -name "*.log.gz" -exec ls -l {} \; | awk '{sum += $5} END {print sum}')

echo "当前日志文件数: $TOTAL_LOGS"
echo "备份文件数: $TOTAL_BACKUPS"
echo "日志占用空间: $(numfmt --to=iec $TOTAL_SIZE)"
echo "备份占用空间: $(numfmt --to=iec $BACKUP_SIZE)"
echo ""

# 生成清理报告
REPORT_FILE="$LOG_DIR/cleanup_report_${TIMESTAMP}.txt"
cat > "$REPORT_FILE" << EOF
AI中转站选型系统 - 日志清理报告
清理时间: $(date)
保留天数: $KEEP_DAYS
==================

清理统计:
- 清理过期日志: $OLD_COUNT 个
- 清理旧备份: $BACKUP_OLD_COUNT 个
- 当前日志文件: $TOTAL_LOGS 个
- 当前备份文件: $TOTAL_BACKUPS 个
- 日志占用空间: $(numfmt --to=iec $TOTAL_SIZE)
- 备份占用空间: $(numfmt --to=iec $BACKUP_SIZE)

清理文件列表:
$(find "$LOG_DIR" -name "*.log" -mtime +$KEEP_DAYS 2>/dev/null | sed 's/^/- /')

备份文件列表:
$(find "$BACKUP_DIR" -name "*.log.gz" 2>/dev/null | sed 's/^/- /')
EOF

echo "📄 清理报告已保存: $REPORT_FILE"
echo ""
echo "✅ 日志清理完成！"