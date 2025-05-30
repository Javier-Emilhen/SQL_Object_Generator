# 🧠 SQL Object Generator

A desktop application built with [Flet](https://flet.dev) and Python that generates SQL Server object definitions (stored procedures, functions, tables, etc.) and allows you to recreate them easily in another database.

---

## 🚀 Features

- 🔍 Scans a SQL Server database
- 📄 Generates creation scripts for:
  - Stored Procedures
  - Functions
  - Tables
- 💾 Configurable and exportable settings
- 🎛 Simple graphical interface using Flet

---

## 🖥 Requirements

- Python 3.10 or higher
- SQL Server
- ODBC Driver for SQL Server installed
- Packages listed in `requirements.txt`


## Notes
---
The config.json file located in src/config/ contains the editable connection string:
{
    "db_config": {
        "server": "servername",
        "username": "username",
        "password": "password",
        "database": "database"
    }
}


## 👨‍💻 Author
Developed by Javier Emilhen Rodríguez González 

## GitHub
[GitHub](https://github.com/Javier-Emilhen)
[Project](https://github.com/Javier-Emilhen/SQL_Object_Generator)
