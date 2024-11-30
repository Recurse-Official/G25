# from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class UserToken(Base):
    __tablename__ = "user_tokens"
    # id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, primary_key=True, index=True)
    user_name = Column(String, index=True)
    token = Column(String, index=True)

Base.metadata.create_all(bind=engine)

# def get_db():
#     return db
    # try:
    #     yield db
    # finally:
    #     db.close()

def save_token(user_id: str, user_name: str, token: str, db: Session = None):
    if not db:
        db = SessionLocal()
    try:
        db_token = UserToken(user_id=user_id, user_name = user_name , token=token)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        db.close()
        print(f"Token saved for user:{user_id}\n,username:{user_name},\n token: {token}")
    except IntegrityError as e:
        db.rollback()
        print(f"Token already exists for user:{user_id} ,username:{user_name}, token: {token}")
        # db_token = None
        #delete the previous token and save the new one
        db_token = db.query(UserToken).filter(UserToken.user_id == user_id).first()
        db.delete(db_token)
        db.commit()
        save_token(user_id, user_name, token, db)

    return db_token


def read_token(user_id: int, db: Session = None):
    if not db:
        db = SessionLocal()
    db_token = db.query(UserToken).filter(UserToken.user_id == user_id).first()
    #print the results
    if db_token:
        print(f"Token read for user:{db_token.user_id}, ,username:{db_token.user_name}\n token: {db_token.token}")
    db.close()
    return db_token # can return None.


def delete_record(user_id: int, db: Session = None):
    if not db:
        db = SessionLocal()
    db_token = db.query(UserToken).filter(UserToken.user_id == user_id).first()
    if db_token:
        db.delete(db_token)
        db.commit()
        print(f"in delete token, Token deleted for user:{db_token.user_id}\n token: {db_token.token}")
    else:
        print(f"in delete token, Token not found for user:{user_id}")
    db.close()
    return db_token