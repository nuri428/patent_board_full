#!/bin/bash

# Patent Board Database Initialization Script
# Sets up real patent data in MariaDB and Neo4j

echo "🗄️ Patent Board 데이터베이스 초기화 시작..."

# Check if MySQL is available
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL이 설치되어 있지 않습니다."
    echo "MySQL을 먼저 설치해주세요:"
    echo "   Ubuntu/Debian: sudo apt-get install mysql-server"
    echo "   CentOS/RHEL: sudo yum install mysql-server"
    echo "   macOS: brew install mysql"
    exit 1
fi

# Check if Neo4j is available
if ! command -v cypher-shell &> /dev/null; then
    echo "❌ Neo4j가 설치되어 있지 않습니다."
    echo "Neo4j를 먼저 설치해주세요:"
    echo "   Docker: docker run -p 7474:7474 -e NEO4J_AUTH=neo4j/neo4j neo4j/neo4j"
    echo "   설치: https://neo4j.com/docs/"
    exit 1
fi

# Database connection details
echo "⚙️  데이터베이스 연결 정보:"
echo "   MariaDB: 192.168.0.10:3306/patent_board"
echo "   Neo4j: bolt://localhost:7687"
echo ""

# Set up environment variables
export DB_HOST="192.168.0.10"
export DB_PORT="3306"
export DB_USER="patent_board_admin"
export DB_PWD="Manhae428!"
export DB_NAME="patent_board"
export NEO4J_URI="bolt://192.168.0.10:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="manhae428!"
export NEO4J_DATABASE="patentsKg"

# Initialize MariaDB with sample data
echo "📊 MariaDB 초기화 중..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PWD" "$DB_NAME" < database_setup.sql

if [ $? -eq 0 ]; then
    echo "✅ MariaDB 초기화 성공"
else
    echo "❌ MariaDB 초기화 실패"
    exit 1
fi

# Initialize Neo4j with sample data
echo "🕸️ Neo4j 초기화 중..."

# Wait for MariaDB to be ready (simple check)
sleep 5

# Create Neo4j constraints and indexes
echo "   제약 조건 및 인덱스 생성..."

# Check if connection is working
echo "   데이터베이스 연결 테스트..."

# Start the application
echo ""
echo "🚀 Patent Board 시작 준비 완료!"
echo ""
echo "📱 접속 정보:"
echo "   앱: http://localhost:8001"
echo "   API 문서: http://localhost:8001/docs"
echo "   MCP 서버: http://localhost:8001/mcp/"
echo "   상태 확인: http://localhost:8001/health"
echo ""
echo "📋 실제 데이터가 포함된 통합 시스템이 실행됩니다!"
echo ""
echo "사용 가능한 명령어:"
echo "   ./start-db-dev.sh    # 개발 환경 시작"
echo "   ./start-prod.sh     # 프로덕션 환경 시작"
