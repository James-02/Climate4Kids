## Climate 4 Kids Flask Web Application

To run the Flask server with the terminal:
- run `cd Stage2-Team-Project`
- run `pip install -r requirements.txt`
- On Windows systems run `python app.py` on Mac/Unix systems run `python3 app.py`
- Go to `http://127.0.0.1:5000/` 



# Important
* For full functionality register a teacher account with an accessible email.
* The project is currently using a local sqlite3 db as it is easier for development however MySQL is fully implemented to use if necessary.
* If the db tables are required to be generated again run these commands within an active Python Console:
```
from app import db
from models import init_db
init_db()
```

# REPO
https://github.com/HarryHamilton/Stage2-Team-Project
