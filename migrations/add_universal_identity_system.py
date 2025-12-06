"""
迁移脚本：添加Universal Identity System
支持多平台身份认证
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from shared.database.connection import sync_engine

def upgrade():
    """执行迁移"""
    with sync_engine.connect() as conn:
        # 1. 添加新字段到users表
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS uuid UUID UNIQUE DEFAULT gen_random_uuid(),
            ADD COLUMN IF NOT EXISTS wallet_address VARCHAR(255),
            ADD COLUMN IF NOT EXISTS wallet_network VARCHAR(50),
            ADD COLUMN IF NOT EXISTS referrer_id INTEGER REFERENCES users(id),
            ADD COLUMN IF NOT EXISTS referral_code VARCHAR(20) UNIQUE,
            ADD COLUMN IF NOT EXISTS total_referrals INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS tier1_commission DECIMAL(5, 2) DEFAULT 0.10,
            ADD COLUMN IF NOT EXISTS tier2_commission DECIMAL(5, 2) DEFAULT 0.05,
            ADD COLUMN IF NOT EXISTS primary_platform VARCHAR(20),
            ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS kyc_status VARCHAR(20) DEFAULT 'pending',
            ADD COLUMN IF NOT EXISTS kyc_verified_at TIMESTAMP;
        """))
        
        # 2. 创建user_identities表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_identities (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                provider VARCHAR(50) NOT NULL,
                provider_user_id VARCHAR(255) NOT NULL,
                provider_data JSONB,
                is_primary BOOLEAN DEFAULT FALSE,
                verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(provider, provider_user_id)
            );
        """))
        
        # 3. 创建account_links表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS account_links (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                link_token VARCHAR(64) UNIQUE NOT NULL,
                link_type VARCHAR(20) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used_at TIMESTAMP,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # 4. 创建索引
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_identities_user_id 
            ON user_identities(user_id);
            
            CREATE INDEX IF NOT EXISTS idx_user_identities_provider 
            ON user_identities(provider, provider_user_id);
            
            CREATE INDEX IF NOT EXISTS idx_users_referral_code 
            ON users(referral_code);
            
            CREATE INDEX IF NOT EXISTS idx_account_links_token 
            ON account_links(link_token);
        """))
        
        # 5. 迁移现有Telegram用户到user_identities
        conn.execute(text("""
            INSERT INTO user_identities (user_id, provider, provider_user_id, is_primary, verified_at)
            SELECT id, 'telegram', tg_id::text, TRUE, created_at
            FROM users
            WHERE tg_id IS NOT NULL
            ON CONFLICT (provider, provider_user_id) DO NOTHING;
        """))
        
        # 6. 生成referral_code（如果还没有）
        conn.execute(text("""
            UPDATE users
            SET referral_code = 'REF' || LPAD(id::text, 8, '0')
            WHERE referral_code IS NULL;
        """))
        
        conn.commit()
        print("✅ Universal Identity System migration completed")

def downgrade():
    """回滚迁移"""
    with sync_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS account_links CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS user_identities CASCADE;"))
        conn.execute(text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS uuid,
            DROP COLUMN IF EXISTS wallet_address,
            DROP COLUMN IF EXISTS wallet_network,
            DROP COLUMN IF EXISTS referrer_id,
            DROP COLUMN IF EXISTS referral_code,
            DROP COLUMN IF EXISTS total_referrals,
            DROP COLUMN IF EXISTS tier1_commission,
            DROP COLUMN IF EXISTS tier2_commission,
            DROP COLUMN IF EXISTS primary_platform,
            DROP COLUMN IF EXISTS last_active_at,
            DROP COLUMN IF EXISTS kyc_status,
            DROP COLUMN IF EXISTS kyc_verified_at;
        """))
        conn.commit()
        print("✅ Rollback completed")

if __name__ == "__main__":
    upgrade()

