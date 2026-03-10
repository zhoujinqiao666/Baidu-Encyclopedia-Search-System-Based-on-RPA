import pymysql
import json
from datetime import datetime
from pymysql.err import OperationalError
import os
from dotenv import load_dotenv
load_dotenv()



class Database:
    """数据库操作类 - 直接用SQL语句"""

    def __init__(self):
        """初始化数据库连接"""
        self.config = {
            'host':     os.getenv('DB_HOST', 'localhost'),
            'port':     int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME', 'baike_rpa'),
            'user':     os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset':  'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
        }
        self.connection = self._connect()

    def _connect(self):
        """建立数据库连接"""
        config = {**self.config, 'connect_timeout': 10}
        return pymysql.connect(**config)

    def _get_cursor(self):
        """获取游标，断线自动重连"""
        try:
            self.connection.ping(reconnect=True)
        except Exception:
            try:
                self.connection = self._connect()
            except Exception as e:
                raise RuntimeError(f"数据库重连失败: {e}")
        return self.connection.cursor()

    def init_tables(self):
        """初始化表（如果不存在就创建）"""
        cursor = self._get_cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
                total_count INT DEFAULT 0 COMMENT '总词条数',
                completed_count INT DEFAULT 0 COMMENT '已完成数',
                success_count INT DEFAULT 0 COMMENT '成功数',
                failed_count INT DEFAULT 0 COMMENT '失败数',
                current_index INT DEFAULT 0 COMMENT '当前处理到第几个',
                current_keyword VARCHAR(200) COMMENT '当前关键词',
                status VARCHAR(20) DEFAULT 'pending' COMMENT '状态',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id INT NOT NULL COMMENT '所属任务ID',
                keyword VARCHAR(200) NOT NULL COMMENT '关键词',
                status VARCHAR(20) DEFAULT 'pending' COMMENT '状态',
                title VARCHAR(500) COMMENT '标题',
                summary TEXT COMMENT '摘要',
                infobox TEXT COMMENT '基本信息(JSON)',
                url VARCHAR(500) COMMENT '链接',
                source VARCHAR(50) DEFAULT '百度百科' COMMENT '来源',
                error_msg TEXT COMMENT '错误信息',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 兼容旧数据库：如果 source 列不存在就自动添加
        try:
            cursor.execute("""
                ALTER TABLE task_items
                ADD COLUMN source VARCHAR(50) DEFAULT '百度百科' COMMENT '来源'
            """)
            self.connection.commit()
            print("✅ source 字段已添加")
        except Exception:
            pass  # 列已存在会抛异常，忽略即可

        self.connection.commit()
        print("✅ 表创建完成")
        cursor.close()

    def create_task(self, task_name, keywords):
        """创建新任务，返回新任务的id"""
        cursor = self._get_cursor()

        cursor.execute("""
            INSERT INTO tasks (task_name, total_count, status)
            VALUES (%s, %s, 'pending')
        """, (task_name, len(keywords)))
        task_id = cursor.lastrowid

        for kw in keywords:
            cursor.execute("""
                INSERT INTO task_items (task_id, keyword, status)
                VALUES (%s, %s, 'pending')
            """, (task_id, kw))

        self.connection.commit()
        cursor.close()
        return task_id

    def get_task(self, task_id):
        """获取任务信息"""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        cursor.close()
        return task

    def get_all_tasks(self):
        """获取所有任务"""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        cursor.close()
        return tasks

    def update_task_progress(self, task_id, current_index, current_keyword):
        """更新任务进度，同时将状态置为 running"""
        cursor = self._get_cursor()
        cursor.execute("""
            UPDATE tasks
            SET current_index = %s,
                current_keyword = %s,
                status = 'running'
            WHERE id = %s
        """, (current_index, current_keyword, task_id))
        self.connection.commit()
        cursor.close()

    def update_item_result(self, item_id, result_data):
        """更新单个词条的结果"""
        cursor = self._get_cursor()

        if result_data.get('success'):
            cursor.execute("""
                UPDATE task_items
                SET status = 'success',
                    title = %s,
                    summary = %s,
                    infobox = %s,
                    url = %s,
                    source = %s
                WHERE id = %s
            """, (
                result_data.get('title', ''),
                result_data.get('summary', ''),
                json.dumps(result_data.get('infobox', {}), ensure_ascii=False),
                result_data.get('url', ''),
                result_data.get('source', '百度百科'),
                item_id
            ))
        else:
            cursor.execute("""
                UPDATE task_items
                SET status = 'failed',
                    error_msg = %s
                WHERE id = %s
            """, (result_data.get('error', '未知错误'), item_id))

        self.connection.commit()
        cursor.close()

    def update_task_counts(self, task_id):
        """更新任务统计数字，并在全部完成时将状态置为 completed"""  # ✅ 修复状态永远是pending的问题
        cursor = self._get_cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as completed,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status = 'failed'  THEN 1 ELSE 0 END) as failed
            FROM task_items
            WHERE task_id = %s AND status != 'pending'
        """, (task_id,))
        counts = cursor.fetchone()

        # 判断是否全部处理完毕
        cursor.execute(
            "SELECT total_count FROM tasks WHERE id = %s", (task_id,)
        )
        task = cursor.fetchone()
        completed = counts['completed'] or 0
        total = task['total_count'] if task else 0
        new_status = 'completed' if completed >= total and total > 0 else 'running'

        cursor.execute("""
            UPDATE tasks
            SET completed_count = %s,
                success_count   = %s,
                failed_count    = %s,
                status          = %s
            WHERE id = %s
        """, (completed, counts['success'] or 0, counts['failed'] or 0, new_status, task_id))

        self.connection.commit()
        cursor.close()

    def get_task_items(self, task_id, status=None):
        """获取任务的所有词条"""
        cursor = self._get_cursor()
        if status:
            cursor.execute("""
                SELECT * FROM task_items
                WHERE task_id = %s AND status = %s
                ORDER BY id
            """, (task_id, status))
        else:
            cursor.execute("""
                SELECT * FROM task_items
                WHERE task_id = %s
                ORDER BY id
            """, (task_id,))
        items = cursor.fetchall()
        cursor.close()
        return items

    def get_task_with_items(self, task_id):
        """获取任务信息及其所有词条（一次性）"""
        cursor = self._get_cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        if task:
            cursor.execute("""
                SELECT * FROM task_items
                WHERE task_id = %s
                ORDER BY id
            """, (task_id,))
            task['items'] = cursor.fetchall()
        cursor.close()
        return task


    def update_task_total(self, task_id, total):
        """抓完后更新任务的实际总词条数"""
        cursor = self._get_cursor()
        cursor.execute(
            "UPDATE tasks SET total_count = %s WHERE id = %s",
            (total, task_id)
        )
        self.connection.commit()
        cursor.close()

    def add_task_item(self, task_id, keyword):
        """向已有任务追加一条词条，返回新 item 的 id"""
        cursor = self._get_cursor()
        cursor.execute(
            "INSERT INTO task_items (task_id, keyword, status) VALUES (%s, %s, 'pending')",
            (task_id, keyword)
        )
        new_id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return new_id


    def get_dashboard_stats(self):
        """获取控制台所需的统计数据"""
        cursor = self._get_cursor()

        # 总词条数、成功数、失败数
        cursor.execute("""
            SELECT
                COUNT(*) as total_items,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_items,
                SUM(CASE WHEN status = 'failed'  THEN 1 ELSE 0 END) as failed_items
            FROM task_items
        """)
        item_stats = cursor.fetchone()

        # 总任务数
        cursor.execute("SELECT COUNT(*) as total_tasks FROM tasks")
        task_stats = cursor.fetchone()

        # 今日搜索数（今天创建的 task_items）
        cursor.execute("""
            SELECT COUNT(*) as today_items
            FROM task_items
            WHERE DATE(created_at) = CURDATE()
        """)
        today_stats = cursor.fetchone()

        # 最近5条任务
        cursor.execute("""
            SELECT id, task_name, status, total_count, success_count,
                   failed_count, completed_count, created_at
            FROM tasks
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_tasks = cursor.fetchall()

        # 计算进度
        for task in recent_tasks:
            total = task['total_count']
            task['progress'] = int(task['completed_count'] / total * 100) if total > 0 else 0
            # 格式化时间为字符串
            if task['created_at']:
                task['created_at'] = task['created_at'].strftime('%Y-%m-%d %H:%M')

        cursor.close()

        total   = item_stats['total_items']   or 0
        success = item_stats['success_items'] or 0

        return {
            'total_tasks':   task_stats['total_tasks']    or 0,
            'total_items':   total,
            'success_items': success,
            'failed_items':  item_stats['failed_items']   or 0,
            'today_items':   today_stats['today_items']   or 0,
            'success_rate':  round(success / total * 100) if total > 0 else 0,
            'recent_tasks':  recent_tasks
        }

    def get_task_statistics(self, task_id):   
        """获取任务的统计信息"""
        cursor = self._get_cursor()
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status = 'failed'  THEN 1 ELSE 0 END) as failed
            FROM task_items
            WHERE task_id = %s
        """, (task_id,))
        stats = cursor.fetchone()
        cursor.close()
        return stats

    def delete_task(self, task_id):           
        """删除任务（级联删除所有词条）"""
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        self.connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected > 0

    def get_source_stats(self):
        """统计各来源词条数量，用于饼图"""
        cursor = self._get_cursor()
        cursor.execute("""
            SELECT
                COALESCE(source, '百度百科') as source,
                COUNT(*) as count
            FROM task_items
            WHERE status = 'success'
            GROUP BY source
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        # 确保三个来源都有值（没有的补0）
        source_map = {r['source']: int(r['count']) for r in rows}
        return [
            {'name': '百度百科',   'value': source_map.get('百度百科',   0)},
            {'name': '墨鱼词典',   'value': source_map.get('墨鱼词典',   0)},
            {'name': 'DeepSeek AI','value': source_map.get('DeepSeek AI', 0)},
        ]

    def get_weekly_stats(self):
        """获取近7天每天的检索量（成功/失败分开），用于折线图"""
        cursor = self._get_cursor()
        cursor.execute("""
            SELECT
                DATE(created_at) as date,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                SUM(CASE WHEN status = 'failed'  THEN 1 ELSE 0 END) as failed
            FROM task_items
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """)
        rows = cursor.fetchall()
        cursor.close()

        # 补全近7天（没数据的天填0）
        from datetime import date, timedelta
        date_map = {str(r['date']): r for r in rows}
        result = []
        for i in range(6, -1, -1):
            d = str(date.today() - timedelta(days=i))
            r = date_map.get(d, {})
            result.append({
                'date':    d,
                'label':   f"{int(d[5:7])}/{int(d[8:])}",   # 格式：3/6
                'success': int(r.get('success') or 0),
                'failed':  int(r.get('failed')  or 0),
            })
        return result

    def close(self):
        """关闭数据库连接"""
        self.connection.close()