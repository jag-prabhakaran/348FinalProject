import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Date, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from datetime import datetime


engine = create_engine('sqlite:///data.db', echo=True)
#engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

Base = declarative_base()
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)

class Task(Base):
    __tablename__ = 'taskstable'
    task_title = Column(String, primary_key=True)
    task_priority = Column(String)
    task_status = Column(String)
    task_due_date = Column(Date)
    task_description = Column(String)

class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)


conn = sqlite3.connect('data.db', check_same_thread=False)

# ORM FUNCTIONS ARE HERE !!
def add_data(task_title, task_priority, task_status, task_due_date, task_description):
    #Ensure Session is automatically closed
    with DBSession() as session:
        try:
            new_task = Task(task_title=task_title, task_priority=task_priority, task_status=task_status, 
                            task_due_date=task_due_date, task_description=task_description)
            session.add(new_task)
            session.commit()
        except:
            session.rollback()
            raise



def filter_tasks_by_priority(priority):
    session = DBSession()
    tasks = session.query(Task).filter(Task.task_priority == priority).all()
    tasks_data = [[task.task_title, task.task_priority, task.task_status, task.task_due_date, task.task_description] for task in tasks]
    session.close()
    return tasks_data


def task_summary_by_status():
    session = DBSession()
    task_count = session.query(Task.task_status, func.count(Task.task_title)).group_by(Task.task_status).all()
    session.close()
    return task_count




# PREPARED STATEMENT FUNTIONS ARE HERE!!
def view_all_data(sort_by=None):
    c = conn.cursor()
    if sort_by == "Priority":
        c.execute('SELECT * FROM taskstable ORDER BY CASE WHEN task_priority="High" THEN 1 WHEN task_priority="Medium" THEN 2 ELSE 3 END, task_due_date')
    elif sort_by == "Due Date":
        c.execute('SELECT * FROM taskstable ORDER BY task_due_date')
    else:
        c.execute('SELECT * FROM taskstable')
    data = c.fetchall()
    c.close()
    return data

def view_all_task_titles():
    c = conn.cursor()
    c.execute('SELECT DISTINCT task_title FROM taskstable')
    data = c.fetchall()
    c.close()
    return data

def get_task(task_title):
    c = conn.cursor()
    c.execute('SELECT * FROM taskstable WHERE task_title=?', (task_title,))
    data = c.fetchone()
    c.close()
    return data

def delete_data(task_title):
    with DBSession() as session:
        try:
            task_to_delete = session.query(Task).filter_by(task_title=task_title).one()
            session.delete(task_to_delete)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


def edit_task_data(new_task_title, new_task_priority, new_task_status, new_task_due_date, new_task_description, original_task_title):
    with DBSession() as session:
        try:
            task = session.query(Task).filter_by(task_title=original_task_title).one()
            task.task_title = new_task_title
            task.task_priority = new_task_priority
            task.task_status = new_task_status
            task.task_due_date = new_task_due_date
            task.task_description = new_task_description
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        
        
        


# User Data functions
def create_user(username, password):
    session = DBSession()
    user_exists = session.query(User).filter_by(username=username).first()
    if not user_exists:
        new_user = User(username=username, password=password)
        session.add(new_user)
        session.commit()
        session.close()
        return True
    session.close()
    return False

def authenticate_user(username, password):
    session = DBSession()
    user = session.query(User).filter_by(username=username, password=password).first()
    session.close()
    return user is not None
