from fastapi import APIRouter,HTTPException
from models.data_models import createDb, addRepo, getDataRequest, getDataResponse, RemoveRepo
import sqlite3
import logging
import os
from fastapi import Body

router=APIRouter()

@router.post("/create_database")
def create_database(createDbRequest : createDb):
    try:
        # Use path joining for cross-platform compatibility
        db_path = os.path.join("backend/database", f"{createDbRequest.name}.db")
        print(db_path)
        # Check if the database already exists
        if os.path.exists(db_path):
            return {"message": "Database already exists"}

        # Create the database
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            cursor.execute(
                "CREATE TABLE repos (id TEXT PRIMARY KEY, name TEXT, full_name TEXT, is_active TEXT, backend_path TEXT)"
            )
            db.commit()
            logging.info("Database created")
            return {"message": "Database created successfully"}
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return {"message": f"Database error: {str(e)}"}

@router.post("/add_repo")
def add_user(addRepoRequest : addRepo):
    try:
        db_path = os.path.join("backend/database", f"repos.db")
        with sqlite3.connect(db_path) as db:
            cursor=db.cursor()
            cursor.execute("INSERT INTO repos (id, name, full_name, is_active, backend_path) VALUES (?,?,?,?,?)",(addRepoRequest.id, addRepoRequest.name, addRepoRequest.full_name, addRepoRequest.is_active, addRepoRequest.backend_path))
            db.commit()
            logging.info("Repo added")
            return {"Message": "Repo added successfully"}
        
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return {"Message": f"Database error: {str(e)}"}
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"Message": f"Unexpected error: {str(e)}"}
    
@router.delete("/remove_repo")
def remove_repo(id: str):
    try:
        db_path = os.path.join("backend/database", "repos.db")
        print("Delete Repo", id)
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            
            # Check if repo exists before attempting deletion
            cursor.execute("SELECT id FROM repos WHERE id = ?", (id,))
            if not cursor.fetchone():
                return {"Message": "Repository not found"}
            
            cursor.execute("DELETE FROM repos WHERE id = ?", (id,))
            db.commit()
            
            if cursor.rowcount > 0:
                logging.info("Repo removed")
                return {"Message": "Repository removed successfully"}
            else:
                return {"Message": "No repository was removed"}
                
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return {"Message": f"Database error: {str(e)}"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"Message": f"Unexpected error: {str(e)}"}
    
@router.get("/get_data")
def get_data(getdatarequest: getDataRequest):
    try:
        # Use path joining for cross-platform compatibility
        db_path = os.path.join("backend/database", "repos.db")

        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute("SELECT * FROM repos WHERE id = ?", (getdatarequest.id,))
            data = cursor.fetchone()

            if not data:
                return {"message": "No data found"}

            return getDataResponse(
                id=data[0],
                name=data[1],
                full_name=data[2],
                is_active=data[3],
                backend_path=data[4],
            )

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return {"message": f"Database error: {str(e)}"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"message": f"Unexpected error: {str(e)}"}
