import mysql.connector
from typing import Dict, List, Tuple
from tabulate import tabulate  # 用于美化表格输出

def get_database_info() -> Dict[str, List[Dict]]:
    """获取数据库所有表的结构信息"""
    try:
        # 连接到 MySQL 数据库
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="5kuo4678K",
            database="fyp_db"
        )
        cursor = conn.cursor(dictionary=True)

        # 获取所有表名
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        table_info = {}
        for table in tables:
            table_name = list(table.values())[0]
            # 获取表结构
            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()
            
            # 获取表注释
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME, 
                    COLUMN_COMMENT
                FROM 
                    INFORMATION_SCHEMA.COLUMNS 
                WHERE 
                    TABLE_SCHEMA = 'fyp_db' 
                    AND TABLE_NAME = '{table_name}'
            """)
            comments = {row['COLUMN_NAME']: row['COLUMN_COMMENT'] for row in cursor.fetchall()}
            
            # 将注释添加到列信息中
            for col in columns:
                col['Comment'] = comments.get(col['Field'], '')
            
            table_info[table_name] = columns

        cursor.close()
        conn.close()
        return table_info

    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return {}

def print_table_structure():
    """打印数据库表结构"""
    table_info = get_database_info()
    
    if not table_info:
        print("未找到任何表结构信息")
        return

    print("\n=== fyp_db 数据库表结构信息 ===\n")
    
    for table_name, columns in table_info.items():
        print(f"\n表名: {table_name}")
        print("-" * 120)
        print(f"{'字段名':<20} {'类型':<20} {'可空':<8} {'键':<8} {'默认值':<20} {'额外信息':<20} {'注释':<20}")
        print("-" * 120)
        
        for col in columns:
            field = col['Field']
            type_ = col['Type']
            null = "是" if col['Null'] == 'YES' else "否"
            key = col['Key'] if col['Key'] else '无'
            default = str(col['Default']) if col['Default'] is not None else "无"
            extra = col['Extra'] if col['Extra'] else '无'
            comment = col['Comment'] if col['Comment'] else '无'
            
            print(f"{field:<20} {type_:<20} {null:<8} {key:<8} {default:<20} {extra:<20} {comment:<20}")
        
        print("\n")

def print_table_data():
    """打印所有表中的数据"""
    try:
        # 连接到 MySQL 数据库
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="5kuo4678K",
            database="fyp_db"
        )
        cursor = conn.cursor(dictionary=True)

        # 获取所有表名
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        print("\n=== fyp_db 数据库表数据 ===\n")

        for table in tables:
            table_name = list(table.values())[0]
            print(f"\n表名: {table_name}")
            print("-" * 80)

            # 获取表的所有数据
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            if not rows:
                print("表中没有数据")
                continue

            # 获取列名
            headers = list(rows[0].keys())
            
            # 将字典列表转换为列表列表
            data = []
            for row in rows:
                data.append([str(row[header]) for header in headers])
            
            # 使用 tabulate 美化输出
            print(tabulate(data, headers=headers, tablefmt="grid"))
            print(f"\n总记录数: {len(rows)}")
            print("\n")

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")

if __name__ == "__main__":
    print_table_structure()
    print_table_data() 