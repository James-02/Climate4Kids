## Climate4Kids Flask Web Application

To run the Flask server with the terminal:
- Move into dir `cd Climate4Kids`
- Build with `make`
- Run with `make run`
- Go to `http://127.0.0.1:5000/`

# Cleaning
You can clean the directory of pycache and .pyc/.pyo files with: `make clean`

You can also clean the directory of everything generated upon building with `make cleanall` 
Be careful, this will remove your venv, sqlite.db and .env

# Important
* For full functionality register a teacher account with an accessible email.
* The project is currently using a local sqlite3 db as it is easier for development however MySQL is fully implemented to use if necessary.

# REPO
https://github.com/James-02/Climate4Kids
