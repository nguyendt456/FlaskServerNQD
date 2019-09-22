from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
engine = create_engine('mysql://root:nguyen@127.0.0.1/nguyen')
meta = MetaData()

user = Table(
   'UserLogin', meta, 
   Column('id', Integer, primary_key = True), 
   Column('username', String), 
   Column('password', String), 
)

s = user.select()
conn = engine.connect()
result = conn.execute(s)

for row in result:
   print (type(row.id))
