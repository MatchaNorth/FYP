from app import app, db
from sqlalchemy import text

def update_database():
    with app.app_context():
        # 添加小黑盒相关字段
        with db.engine.connect() as conn:
            # MySQL不支持IF NOT EXISTS，所以我们需要分别执行每个ALTER语句
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN heybox_id VARCHAR(20)"))
            except:
                pass
                
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN heybox_nickname VARCHAR(80)"))
            except:
                pass
                
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN heybox_avatar VARCHAR(255)"))
            except:
                pass
                
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN heybox_profile VARCHAR(255)"))
            except:
                pass
                
            conn.commit()
        print("数据库更新成功！")

if __name__ == '__main__':
    update_database() 