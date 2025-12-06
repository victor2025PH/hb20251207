"""
直接使用 SQLite 添加字段（不依赖复杂导入）
"""
import sqlite3
import sys
from pathlib import Path

# 查找数据库文件
project_root = Path(__file__).resolve().parent

# 可能的数据库文件位置
possible_db_paths = [
    project_root / "luckyred.db",
    project_root / "data" / "luckyred.db",
    project_root / "database.db",
    project_root / "bot" / "luckyred.db",
]

db_path = None
for path in possible_db_paths:
    if path.exists():
        db_path = path
        break

if not db_path:
    # 尝试从 .env 读取
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if url.startswith("sqlite:///"):
                        db_path_str = url.replace("sqlite:///", "")
                        if db_path_str.startswith("./"):
                            db_path = project_root / db_path_str[2:]
                        else:
                            db_path = Path(db_path_str)
                    break

if not db_path or not db_path.exists():
    print("❌ 找不到数据库文件")
    print("请检查 .env 文件中的 DATABASE_URL")
    sys.exit(1)

print("=" * 60)
print("数据库迁移 - 添加交互模式字段")
print("=" * 60)
print()
print(f"数据库文件: {db_path}")
print()

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 检查字段是否已存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    print("当前字段:")
    for col in columns:
        print(f"  - {col}")
    print()
    
    required = ['interaction_mode', 'last_interaction_mode', 'seamless_switch_enabled']
    missing = [col for col in required if col not in columns]
    
    if not missing:
        print("✅ 所有字段已存在，无需迁移")
    else:
        print(f"需要添加字段: {', '.join(missing)}")
        print()
        
        # 添加字段
        if 'interaction_mode' not in columns:
            print("添加 interaction_mode...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN interaction_mode VARCHAR(20) DEFAULT 'auto'
            """)
        
        if 'last_interaction_mode' not in columns:
            print("添加 last_interaction_mode...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN last_interaction_mode VARCHAR(20) DEFAULT 'keyboard'
            """)
        
        if 'seamless_switch_enabled' not in columns:
            print("添加 seamless_switch_enabled...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN seamless_switch_enabled INTEGER DEFAULT 1
            """)
        
        conn.commit()
        print()
        print("✅ 成功添加所有字段！")
    
    # 验证
    print()
    print("=" * 60)
    print("验证字段...")
    print("=" * 60)
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    for col in required:
        if col in columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} (缺失)")
    
    print()
    if all(col in columns for col in required):
        print("✅ 迁移成功！所有字段已添加")
    else:
        print("❌ 迁移失败，仍有字段缺失")
    
    conn.close()
    print("=" * 60)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
