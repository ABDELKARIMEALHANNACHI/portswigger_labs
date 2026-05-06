query = "SELECT name FROM products WHERE name LIKE ?"
cur.execute(query, ('%' + q + '%',))
