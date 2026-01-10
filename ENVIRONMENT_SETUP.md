# Patent Board - Environment Configuration Guide

This guide explains the environment variables needed to run the Patent Board application in different environments.

## 🚀 Quick Setup

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Update with your actual values** (see sections below)

3. **Set up databases** (see Database Setup section)

## 📊 Database Setup

### MariaDB (Primary Database)

Create database and user:
```sql
CREATE DATABASE patent_db;
CREATE USER 'patent_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON patent_db.* TO 'patent_user'@'localhost';
FLUSH PRIVILEGES;
```

**Environment Variables:**
```bash
MARIADB_URL=mysql+aiomysql://patent_user:your_secure_password@localhost:3306/patent_db
MARIADB_HOST=localhost
MARIADB_PORT=3306
MARIADB_DATABASE=patent_db
MARIADB_USER=patent_user
MARIADB_PASSWORD=your_secure_password
```

### Neo4j (Graph Database)

Start Neo4j and create constraints:
```bash
# Using Neo4j Desktop or Docker
# Then run these constraints:
CREATE CONSTRAINT patent_id IF NOT EXISTS FOR (p:Patent) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT patent_number IF NOT EXISTS FOR (p:Patent) REQUIRE p.patent_number IS UNIQUE;
CREATE INDEX patent_title IF NOT EXISTS FOR (p:Patent) ON (p.title);
CREATE INDEX patent_assignee IF NOT EXISTS FOR (p:Patent) ON (p.assignee);
```

**Environment Variables:**
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j
```

## 🔐 Security Configuration

### JWT Secret Key

Generate a secure secret key:
```bash
# Generate 32-character hex string
openssl rand -hex 32

# Or using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Environment Variable:**
```bash
SECRET_KEY=your-generated-secret-key-here
```

## 🤖 AI Service Configuration

### OpenAI (for LLM features)

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set environment variables:

```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7
```

### LangSmith (for LangGraph tracing)

1. Create account at [LangSmith](https://smith.langchain.com/)
2. Get API key and create project
3. Set environment variables:

```bash
LANGSMITH_API_KEY=ls-your-langsmith-api-key
LANGSMITH_PROJECT=patent-board
```

## 🌐 Application Configuration

### Server Settings

```bash
# Main application
HOST=0.0.0.0
PORT=8001

# API version prefix
API_V1_STR=/api/v1

# Project info
PROJECT_NAME=Patent Board
VERSION=1.0.0
```

### CORS Configuration

For development:
```bash
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8001,http://127.0.0.1:3000
FRONTEND_URL=http://localhost:3000
```

For production:
```bash
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

## 🔧 Optional Services

### Redis (Caching)

```bash
REDIS_URL=redis://localhost:6379/0
```

### Elasticsearch (Advanced Search)

```bash
ELASTICSEARCH_URL=http://localhost:9200
```

## 🌍 Environment-Specific Settings

### Development

```bash
DEBUG=true
DEVELOPMENT=true
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Production

```bash
DEBUG=false
DEVELOPMENT=false
ENVIRONMENT=production
LOG_LEVEL=WARNING

# Database pooling
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
```

## 🐳 Docker Environment

When using Docker Compose, the environment variables are set in `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - MARIADB_URL=mysql+aiomysql://patent_user:${MARIADB_PASSWORD}@mariadb:3306/patent_db
      - NEO4J_URI=bolt://neo4j:${NEO4J_PASSWORD}@neo4j:7687
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
```

## 🚨 Security Best Practices

1. **Never commit .env files** to version control
2. **Use strong, unique passwords** for all services
3. **Rotate secrets regularly** in production
4. **Use environment-specific configs** (dev/staging/prod)
5. **Enable SSL/TLS** in production environments
6. **Monitor for exposed credentials** in logs

## 🔍 Validation

After setup, validate configuration:

```bash
# Test database connections
python -c "
from shared.database import get_mariadb_db, get_neo4j_db
print('MariaDB: OK' if next(get_mariadb_db()) else 'FAIL')
print('Neo4j: OK' if get_neo4j_db().get_session().run('RETURN 1') else 'FAIL')
"

# Test API startup
uvicorn back_end.app:app --host 0.0.0.0 --port 8001
```

## 📋 Configuration Checklist

- [ ] MariaDB user created with privileges
- [ ] Neo4j constraints created
- [ ] Environment variables copied and updated
- [ ] JWT secret key generated
- [ ] OpenAI API key configured
- [ ] CORS origins set correctly
- [ ] Database connections tested
- [ ] Application starts without errors
- [ ] API docs accessible at http://localhost:8001/docs

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Test MariaDB
mysql -u patenti_user -p -h localhost

# Test Neo4j
cypher-shell -u neo4j -p your_password
```

### Common Errors

1. **"Access denied"**: Check database credentials
2. **"Connection refused"**: Verify database services are running
3. **"CORS error"**: Update BACKEND_CORS_ORIGINS with correct frontend URL
4. **"Invalid JWT"**: Verify SECRET_KEY matches between services