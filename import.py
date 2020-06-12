import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
                                            
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)
next(reader)

Variable_tableName='books'
if not engine.dialect.has_table(engine, Variable_tableName): 
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn TEXT NOT NULL UNIQUE, title TEXT NOT NULL, author TEXT NOT NULL, year TEXT NOT NULL)")
else:
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                        {"isbn": isbn, "title": title, "author": author, "year": year})
        
db.commit()