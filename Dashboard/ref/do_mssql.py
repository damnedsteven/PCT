import pymssql

conn = pymssql.connect("16.187.224.112", "sa", "support", "Aaron")
cursor = conn.cursor(as_dict=True)
cursor.execute("""
IF OBJECT_ID('persons', 'U') IS NOT NULL
    DROP TABLE persons
CREATE TABLE persons (
    id INT NOT NULL,
    name VARCHAR(100),
    salesrep VARCHAR(100),
    PRIMARY KEY(id)
)
""")
cursor.executemany(
    "INSERT INTO persons VALUES (%d, %s, %s)",
    [(1, 'John Smith', 'John Doe'),
     (2, 'Jane Doe', 'Joe Dog'),
     (3, 'Mike T.', 'Sarah H.')])
# you must call commit() to persist your data if you don't set autocommit to True
conn.commit()

cursor.execute('SELECT * FROM persons WHERE salesrep=%s', 'John Doe')

row = cursor.fetchone()
while row:
   print("ID=%d, Name=%s" % (row['id'], row['name']))
   row = cursor.fetchone()

# for row in cursor:
    # print('row = %r' % (row,))

conn.close()
