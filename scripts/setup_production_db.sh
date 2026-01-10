#!/bin/bash

# Patent Board Production Database Setup
# Configures production database connections and optimizations

echo "🚀 Patent Board Production 데이터베이스 설정"

# Production environment variables
export DB_HOST="${DB_HOST:-192.168.0.10}"
export DB_PORT="${DB_PORT:-3306}"
export DB_USER="${DB_USER:-patent_board_admin}"
export DB_PWD="${DB_PWD:-Manhae428!}"
export DB_NAME="${DB_NAME:-patent_board}"
export NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-password}"

# Database optimization settings
export DB_POOL_SIZE="${DB_POOL_SIZE:-20}"
export DB_POOL_TIMEOUT="${DB_POOL_TIMEOUT:-30}"
export NEO4J_MAX_CONNECTIONS="${NEO4J_MAX_CONNECTIONS:-100}"

echo "📋 환경 설정:"
echo "   DB_HOST: $DB_HOST"
echo "   DB_PORT: $DB_PORT" 
echo "   DB_NAME: $DB_NAME"
echo "   NEO4J_URI: $NEO4J_URI"
echo "   DB_POOL_SIZE: $DB_POOL_SIZE"
echo "   NEO4J_MAX_CONNECTIONS: $NEO4J_MAX_CONNECTIONS"

# Database optimizations
echo ""
echo "🔧 MariaDB 최적화 설정:"

# Create optimized my.cnf
cat > /tmp/my.cnf << 'EOF'
[mysqld]
# Connection settings
max_connections = 200
max_connect_errors = 100
wait_timeout = 28800
interactive_timeout = 28800

# InnoDB settings
innodb_buffer_pool_size = 256M
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT

# Query cache
query_cache_type = 1
query_cache_size = 64M

# Binary log
log_bin = 1
binlog_format = ROW
expire_logs_days = 7
max_binlog_size = 100M

# Slow query log
slow_query_log = 1
long_query_time = 2
EOF

echo "   MariaDB 최적화 설정 생성: /tmp/my.cnf"

echo ""
echo "🕸️ Neo4j 최적화 설정:"

# Create Neo4j.conf
cat > /tmp/neo4j.conf << 'EOF'
# Memory settings
server.memory.heap.initial_size=512m
server.memory.heap.max_size=2G

# Connection settings
server.bolt.thread_pool_min_size=5
server.bolt.thread_pool_max_size=200
server.bolt.connection_keep_alive=300s

# Log settings
server.logs.gc.enabled=true
server.logs.gc.rotation.keep_number=10
server.logs.gc.threshold=1m

# Network settings
server.bolt.receivetimeout=120s
server.bolt.sendtimeout=120s

# JVM settings
server.jvm.additional=-XX:+UseG1GC
server.jvm.additional=-Dneo4j.pagecache.memory.ratio=0.9
EOF

echo "   Neo4j 최적화 설정 생성: /tmp/neo4j.conf"

# Backup existing configurations
if [ -f /etc/mysql/my.cnf ]; then
    echo "   기존 MariaDB 설정 백업: /etc/mysql/my.cnf.backup"
    sudo cp /etc/mysql/my.cnf /etc/mysql/my.cnf.backup
fi

if [ -f /etc/neo4j/neo4j.conf ]; then
    echo "   기존 Neo4j 설정 백업: /etc/neo4j/neo4j.conf.backup"
    sudo cp /etc/neo4j/neo4j.conf /etc/neo4j/neo4j.conf.backup
fi

# Apply new configurations
echo ""
echo "⚙️ 새 설정 적용 중..."

# Apply MariaDB configuration
if [ -f /tmp/my.cnf ]; then
    sudo cp /tmp/my.cnf /etc/mysql/my.cnf
    sudo systemctl restart mysql
    echo "   ✅ MariaDB 설정 업데이트 및 재시작"
else
    echo "   ❌ MariaDB 설정 파일 생성 실패"
fi

# Apply Neo4j configuration  
if [ -f /tmp/neo4j.conf ]; then
    if [ -d /etc/neo4j ]; then
        sudo cp /tmp/neo4j.conf /etc/neo4j/neo4j.conf
        sudo systemctl restart neo4j
        echo "   ✅ Neo4j 설정 업데이트 및 재시작"
    else
        echo "   Neo4j 디렉토리 없음. /etc/neo4j 디렉토리 생성 필요"
        sudo mkdir -p /etc/neo4j
        sudo cp /tmp/neo4j.conf /etc/neo4j/neo4j.conf
        sudo systemctl enable neo4j
        sudo systemctl start neo4j
        echo "   ✅ Neo4j 첫 설정 및 서비스 시작"
    fi
else
    echo "   ❌ Neo4j 설정 파일 생성 실패"
fi

echo ""
echo "📊 데이터베이스 성능 설정 완료"
echo "   재시작 명령어: sudo systemctl restart mysql neo4j"
echo ""
echo "🚀 Production 데이터베이스 설정 완료!"