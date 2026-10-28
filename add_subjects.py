from ingestion.db import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("INSERT INTO subjects (id, board_id, class_id, name) VALUES ('tn_10_maths', 'TN_STATE', 'tn_class_10', 'Maths') ON CONFLICT DO NOTHING;")
cur.execute("INSERT INTO subjects (id, board_id, class_id, name) VALUES ('tn_10_social', 'TN_STATE', 'tn_class_10', 'Social Science') ON CONFLICT DO NOTHING;")
conn.commit()
conn.close()
print("Success")
