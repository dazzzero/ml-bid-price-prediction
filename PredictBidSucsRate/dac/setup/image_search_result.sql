CREATE TABLE IF NOT EXISTS image_search_result (
    seq INTEGER PRIMARY KEY AUTOINCREMENT
    , subject TEXT
    , url TEXT NOT NULL
    , keyword TEXT NOT NULL
    , desc TEXT 
    , thumb TEXT
    , thumb2 TEXT
    , subtitle TEXT
    , save_path TEXT
    , save_name TEXT
    , save_ext TEXT
    , save_size NUMERIC NOT NULL DEFAULT(0)
    , org_path TEXT
    , org_name TEXT
    , org_ext TEXT
    , org_size NUMERIC NOT NULL DEFAULT(0)
    , rmk TEXT
    , hash TEXT
    , sortno NUMERIC NOT NULL DEFAULT(0)
    , reg_date TEXT NOT NULL DEFAULT(DATETIME('now', 'localtime'))
);
