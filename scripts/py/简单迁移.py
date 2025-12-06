"""
简单数据库迁移脚本（直接添加字段）
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("数据库迁移 - 添加交互模式字段")
print("=" * 60)
print()

try:
    from shared.database.connection import get_db
    from shared.config.settings import get_settings
    from sqlalchemy import text
    
    settings = get_settings()
    print(f"数据库类型: {'SQLite' if settings.DATABASE_URL.startswith('sqlite') else 'PostgreSQL'}")
    print(f"数据库 URL: {settings.DATABASE_URL[:50]}...")
    print()
    
    with get_db() as db:
        # 检查字段是否已存在（SQLite）
        print("检查字段是否已存在...")
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'interaction_mode' in columns:
            print("✅ 字段已存在，跳过迁移")
        else:
            print("正在添加字段...")
            
            # 添加字段
            print("  - 添加 interaction_mode...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN interaction_mode VARCHAR(20) DEFAULT 'auto'
            """))
            
            print("  - 添加 last_interaction_mode...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN last_interaction_mode VARCHAR(20) DEFAULT 'keyboard'
            """))
            
            print("  - 添加 seamless_switch_enabled...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN seamless_switch_enabled INTEGER DEFAULT 1
            """))
            
            db.commit()
            print()
            print("✅ 成功添加所有字段！")
    
    print()
    print("=" * 60)
    print("验证字段...")
    print("=" * 60)
    
    # 验证
    with get_db() as db:
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        required = ['interaction_mode', 'last_interaction_mode', 'seamless_switch_enabled']
        missing = [col for col in required if col not in columns]
        
        for col in required:
            if col in columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (缺失)")
        
        print()
        if not missing:
            print("✅ 迁移成功！所有字段已添加")
        else:
            print(f"❌ 迁移失败，缺少字段: {', '.join(missing)}")
    
    print("=" * 60)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
