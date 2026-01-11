from sqlalchemy import create_engine, text
from app.core.config import settings


def update_db_mcp():
    db_url = settings.MARIADB_URL.replace("mysql+aiomysql", "mysql+pymysql")
    engine = create_engine(db_url)

    with engine.connect() as conn:
        print("Checking if mcp_api_keys table exists...")
        # Check if table exists
        result = conn.execute(text("SHOW TABLES LIKE 'mcp_api_keys'"))
        if result.fetchone():
            print("Table 'mcp_api_keys' already exists.")
        else:
            print("Creating 'mcp_api_keys' table...")
            conn.execute(
                text("""
                CREATE TABLE mcp_api_keys (
                    id INTEGER NOT NULL AUTO_INCREMENT, 
                    user_id INTEGER NOT NULL, 
                    name VARCHAR(255) NOT NULL, 
                    api_key VARCHAR(255) NOT NULL, 
                    key_type VARCHAR(50) NOT NULL, 
                    is_active BOOL, 
                    created_at DATETIME DEFAULT now(), 
                    last_used_at DATETIME, 
                    PRIMARY KEY (id), 
                    UNIQUE (api_key), 
                    FOREIGN KEY(user_id) REFERENCES users (id)
                )
            """)
            )
            print("Table 'mcp_api_keys' created successfully.")

            # Create index for api_key
            print("Creating index for api_key...")
            conn.execute(
                text("CREATE INDEX ix_mcp_api_keys_api_key ON mcp_api_keys (api_key)")
            )
            print("Index created.")

        conn.commit()


if __name__ == "__main__":
    update_db_mcp()
