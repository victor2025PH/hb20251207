"""
修复SQLite数据库users表tg_id字段，允许为NULL
SQLite不支持直接修改NOT NULL约束，需要重建表
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from shared.config.settings import get_settings

settings = get_settings()


def upgrade():
    """升级数据库（SQLite专用）"""
    # 创建同步引擎
    sync_engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', '').replace('+aiosqlite', ''))
    
    with sync_engine.connect() as conn:
        # 检查数据库类型
        db_url = settings.DATABASE_URL
        is_sqlite_db = 'sqlite' in db_url.lower()
        
        if not is_sqlite_db:
            print("⚠️ 这不是SQLite数据库，请使用fix_tg_id_nullable.py")
            return
        
        inspector = inspect(sync_engine)
        
        # 检查tg_id字段的当前状态
        columns = inspector.get_columns('users')
        tg_id_col = next((col for col in columns if col['name'] == 'tg_id'), None)
        
        if not tg_id_col:
            print("⚠️ 未找到tg_id字段")
            return
        
        if tg_id_col['nullable']:
            print("✅ tg_id字段已经是nullable，无需修改")
            return
        
        print("🔧 SQLite需要重建表来修改NOT NULL约束...")
        print("⚠️ 警告：这将删除所有数据！")
        print("   如果数据库中有重要数据，请先备份！")
        
        # 检查是否有数据
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️ 数据库中有 {count} 条用户记录")
            print("   建议：先备份数据库，然后手动处理")
            print("   或者：使用Alembic迁移工具")
            return
        
        print("✅ 数据库为空，可以安全重建表")
        
        # 开始事务
        trans = conn.begin()
        try:
            # 1. 创建新表（tg_id可为NULL）
            conn.execute(text("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id BIGINT UNIQUE,
                    username VARCHAR(64),
                    first_name VARCHAR(64),
                    last_name VARCHAR(64),
                    language_code VARCHAR(10) DEFAULT 'zh-TW',
                    balance_usdt NUMERIC(20, 8) DEFAULT 0,
                    balance_ton NUMERIC(20, 8) DEFAULT 0,
                    balance_stars BIGINT DEFAULT 0,
                    balance_points BIGINT DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    xp BIGINT DEFAULT 0,
                    invited_by BIGINT,
                    invite_code VARCHAR(16) UNIQUE,
                    invite_count INTEGER DEFAULT 0,
                    invite_earnings NUMERIC(20, 8) DEFAULT 0,
                    last_checkin DATETIME,
                    checkin_streak INTEGER DEFAULT 0,
                    is_banned BOOLEAN DEFAULT 0,
                    is_admin BOOLEAN DEFAULT 0,
                    interaction_mode VARCHAR(20) DEFAULT 'auto',
                    last_interaction_mode VARCHAR(20) DEFAULT 'keyboard',
                    seamless_switch_enabled BOOLEAN DEFAULT 1,
                    uuid VARCHAR(36) UNIQUE,
                    wallet_address VARCHAR(255),
                    wallet_network VARCHAR(50),
                    referrer_id INTEGER REFERENCES users(id),
                    referral_code VARCHAR(20) UNIQUE,
                    total_referrals INTEGER DEFAULT 0,
                    tier1_commission NUMERIC(5, 2) DEFAULT 0.10,
                    tier2_commission NUMERIC(5, 2) DEFAULT 0.05,
                    primary_platform VARCHAR(20),
                    last_active_at DATETIME,
                    kyc_status VARCHAR(20) DEFAULT 'pending',
                    kyc_verified_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 2. 复制数据（如果有）
            if count > 0:
                conn.execute(text("""
                    INSERT INTO users_new SELECT * FROM users;
                """))
            
            # 3. 删除旧表
            conn.execute(text("DROP TABLE users;"))
            
            # 4. 重命名新表
            conn.execute(text("ALTER TABLE users_new RENAME TO users;"))
            
            # 5. 重建索引
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_tg_id ON users(tg_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_invite_code ON users(invite_code);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_referral_code ON users(referral_code);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_uuid ON users(uuid);"))
            
            trans.commit()
            print("✅ 表重建成功，tg_id字段现在可以为NULL")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ 重建表失败: {e}")
            raise


if __name__ == "__main__":
    upgrade()

