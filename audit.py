from config import config
import sqlite3


def print_audit_log():
    with sqlite3.connect(config.db.db_file) as conn:
        cur = conn.execute(
            'SELECT created_at, actor, actor_ip, event_name, event_data FROM audit_log JOIN event_types ON event_types.id = event_type ORDER BY created_at ASC')
        logs = cur.fetchall()

    for log in logs:
        print(log)


if __name__ == '__main__':
    print_audit_log()
