query = "SELECT name FROM products WHERE id = ?"
cur.execute(query, (pid,))
