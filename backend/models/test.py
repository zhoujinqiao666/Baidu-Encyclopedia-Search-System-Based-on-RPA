# backend/test_db_sql.py
# 测试直接用SQL语句操作数据库

from db import Database

print("="*50)
print("测试直接用SQL语句操作数据库")
print("="*50)

# 1. 连接数据库
db = Database()

# 2. 创建表
db.init_tables()

# 3. 创建一个任务
task_id = db.create_task(
    task_name="第一次测试",
    keywords=["武汉纺织大学", "华中科技大学", "武汉大学"]
)
print(f"✅ 创建任务成功，ID: {task_id}")

# 4. 查看任务
task = db.get_task(task_id)
print(f"📋 任务信息: {task}")

# 5. 查看所有任务
tasks = db.get_all_tasks()
print(f"📋 所有任务: {tasks}")

# 6. 更新进度
db.update_task_progress(task_id, 1, "武汉纺织大学")
print("✅ 更新进度成功")

# 7. 查看该任务的所有词条
items = db.get_task_items(task_id)
print(f"📋 词条列表:")
for item in items:
    print(f"   - {item['keyword']} ({item['status']})")

# 8. 关闭连接
db.close()