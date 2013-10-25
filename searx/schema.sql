CREATE TABLE IF NOT EXISTS snippets 
    (id INTEGER PRIMARY KEY ASC AUTOINCREMENT, 
    url TEXT, 
    content TEXT,
    title TEXT);

CREATE TABLE IF NOT EXISTS results 
    (id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    keyword TEXT, 
    snippet INTEGER REFERENCES snippets (id), 
    score INTEGER, 
    UNIQUE (keyword, snippet));
