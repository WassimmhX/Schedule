from pymongo import MongoClient
import pandas as pd
import os
import numpy as np
import bcrypt
import re
import datetime
from dotenv import load_dotenv
import copy
load_dotenv()
def get_db():
    client = MongoClient(os.environ["MONGODB_URL"])
    db = client[os.environ["BD_NAME"]]
    return db
def schedules(db,id=False):
    if id :
        return list(db["schedules"].find())
    else:
        return list(db["schedules"].find({},{"_id":0}))
def add_session(db,data,session):
    schs=db["schedules"]
    classSchedule=schs.find({"class":session["class"],"day":session["day"]})
    teacherSchedule=schs.find({"teacher":session["teacher"],"day":session["day"]})
    roomSchedule=schs.find({"room":session["room"],"day":session["day"]})
    for i in classSchedule:
        if times_overlap(session["time"],i["time"]):
            return "Classe already study in that time",400
    for i in teacherSchedule:
        if times_overlap(session["time"],i["time"]):
            return "Teacher already works in that time",400
    for i in roomSchedule:
        if times_overlap(session["time"],i["time"]):
            return "Room already busy in that time",400
    schs.insert_one(session)
    if "_id" in session:
        session.pop("_id")
    data.append(session)
    return "Added Schedule successfully",200
def getScheduleType(name):
    classes=classes_list(get_db())
    for c in classes:
        if c["name"]==name:
            return "Class"
    teachers=teachers_list(get_db())
    for t in teachers:
        if t["name"]==name:
            return "Teacher"
    rooms=rooms_list(get_db())
    for r in rooms:
        if r["name"]==name:
            return "Room"
    return None
def find_day_of_schedule(data,schedule,day,schedule_type):
    if schedule_type=="Class":
        results = [i for i in data if isinstance(i["class"], str) and (i["class"].strip() in schedule or schedule.strip() in i["class"].strip()) and i["day"]==day]
    elif schedule_type=="Teacher":
        results = [i for i in data if i["teacher"].strip() == schedule.strip() and i["day"]==day]
    else:
        results = [i for i in data if i["room"].strip() == schedule.strip() and i["day"]==day]
    return results
def find_schedule(data,schedule,schedule_type):
    if schedule_type=="Class":
        results = [i for i in data if isinstance(i["class"], str) and (i["class"].strip() in schedule or schedule.strip() in i["class"].strip())]
    elif schedule_type=="Teacher":
        results = [i for i in data if i["teacher"].strip() == schedule.strip()]
    else:
        results = [i for i in data if i["room"].strip() == schedule.strip()]
    return results
def edit_session_time(db,data,newSchedule,resize=False):
    schs = db["schedules"]
    prevSchedule=schs.find({"subject":newSchedule["subject"],"class":newSchedule["class"],"room":newSchedule["room"],"time":newSchedule["id"],"teacher":newSchedule["teacher"]})
    prevSchedule = list(prevSchedule)
    if len(prevSchedule)!=1:
        return "Reload the page if the error persist",400
    prevSchedule=prevSchedule[0]
    if resize:
        schs.delete_one({"_id":prevSchedule["_id"]})
    classSchedule = schs.find({"class": newSchedule["class"], "day": newSchedule["day"]})
    teacherSchedule = schs.find({"teacher": newSchedule["teacher"], "day": newSchedule["day"]})
    roomSchedule = schs.find({"room": newSchedule["room"], "day": newSchedule["day"]})
    for i in classSchedule:
        if times_overlap(newSchedule["time"], i["time"]) and not resize:
            print(newSchedule["time"],i)
            return "Class already have a session in that time", 400
    for i in teacherSchedule:
        if times_overlap(newSchedule["time"], i["time"]):
            return "Teacher already works in that time", 400
    for i in roomSchedule:
        if times_overlap(newSchedule["time"], i["time"]):
            return "Room already busy in that time", 400
    filtered_data = {key: value for key, value in prevSchedule.items() if key != "_id"}
    index=data.index(filtered_data)
    prevSchedule["time"] = newSchedule["time"]
    prevSchedule["day"] = newSchedule["day"]
    schs.update_one({"_id": prevSchedule["_id"]},{"$set":prevSchedule},upsert=True)
    prevSchedule.pop("_id")
    data[index]=prevSchedule
    return "Edited successfully",200
def edit_session_infos(db,data,newSession):
    schs = db["schedules"]
    prevSession=list(schs.find({"time":newSession["time"],"day":newSession["day"],"class":newSession["class"]}))
    if len(prevSession)!=1:
        return "Reload the page if the error persist",400
    prevSession=prevSession[0]

    schs.update_one({"_id":prevSession["_id"]},{"$set":newSession})
    return "Updated successfully",200
def delete_session(db,data,schedule):
    schs=db["schedules"]
    print(schedule)
    schedule.pop("id")
    print(schedule)
    try :
        data.remove(schedule)
        print("hi")
        schs.delete_one(schedule)
        print("heijfz")
        return "Deleted successfully",200
    except:
        return "failed to delete",400

def teachers_list(db,id=False):
    if id :
        return list(db["teachers_list"].find())
    else:
        return list(db["teachers_list"].find({},{"_id":0}))
def teachers_schedule(db,id=False):
    if id :
        return list(db["teachers_schedule"].find())
    else:
        return list(db["teachers_schedule"].find({},{"_id":0}))
def add_teacher(db,teacher):
    teachers = db["teachers_list"]
    if exists(teachers,"email",teacher["email"]):
        return False,"Email already exists",400
    if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', teacher["email"]):
        return "invalid email",400
    if not re.match(r"^[a-zA-Z\s'-]+$",teacher["name"]):
        return "Invalid name",400
    teachers.insert_one(teacher)
    return "success", 200
def updateTeacher(db,teacher):
    if "name" not in teacher or 'email' not in teacher:
        return {"error": "Missing 'data' parameter"}, 400
    if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', teacher["email"]):
        return {"error": "Invalid email"}, 400
    if not re.match(r"^[a-zA-Z\s'-]+$", teacher["name"]):
        return {"error": "Invalid name"}, 400
    teachers=db["teachers_list"]
    if not teachers.find_one({"email":teacher["email"]}):
        return {"error": "Email does not exist"}, 400
    teachers.update_one({"email":teacher["email"]},{"$set":{"name":teacher["name"]}})
    return {'succes': 'updated successfully'}, 200
def deleteTeacher(db,email):
    teachers=db["teachers_list"]
    try:
        teachers.delete_one({"email":email})
        return "deleted successfully",200
    except:
        return  "Email does not exist",400
def nb_teacher(db):
    return db["teachers_list"].count_documents({})

def classes_list(db,id=False):
    if id :
        return list(db["classes_list"].find())
    else:
        return list(db["classes_list"].find({},{"_id":0}))
def classes_schedule(db,id=False):
    if id :
        return list(db["classes_schedule"].find())
    else:
        return list(db["classes_schedule"].find({},{"_id":0}))
def deleteClass(db,name):
    classes=db["classes_list"]
    try:
        classes.delete_one({"name":name})
        return "deleted successfully",200
    except:
        return  "name does not exist",400
def add_class(db,classe):
    classes=db["classes_list"]
    if exists(classes,"name",classe["name"]):
        return "Class already exists", 400
    classes.insert_one({"name":classe["name"]})
    return "success",200
def nb_class(db):
    return db["classes_list"].count_documents({})

def rooms_list(db,id=False):
    if id :
        return list(db["rooms_list"].find())
    else:
        return list(db["rooms_list"].find({},{"_id":0}))
def rooms_schedule(db,id=False):
    if id :
        return list(db["rooms_schedule"].find())
    else:
        return list(db["rooms_schedule"].find({},{"_id":0}))
def add_room(db,room):
    rooms = db["rooms_list"]
    if exists(rooms, "name", room["name"]):
        return "Room already exists",400
    rooms.insert_one(room)
    return "success", 200
def deleteRoom(db,name):
    rooms=db["rooms_list"]
    try:
        rooms.delete_one({"name":name})
        return "deleted successfully",200
    except:
        return  "Room does not exist",400
def nb_room(db):
    return db["rooms_list"].count_documents({})

def users_list(db,id=False):
    if id :
        return list(db["users"].find())
    else:
        return list(db["users"].find({},{"_id":0,"password":0}))
def add_user(db,user):
    users=db["users"]
    if exists(users,"email",user["email"]):
        return "Email already exists",400

    for i in user.keys():
        if user[i]=="" and i!="mySchedule":
            return i+" is empty",400
    if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user["email"]):
        return "invalid email",400
    if len(user["phoneNumber"])!=8:
        return "Invalid phone number",400
    if not re.match(r"^[a-zA-Z\s'-]+$",user["name"]):
        return "Invalid name",400
    if len(user["password"].strip())<4:
        return "Password must be more then 4 characters",400
    user["password"]=hash_password(user["password"])
    users.insert_one(user)
    return "success",200
def verifLogin(db,email,password):
    users=db["users"]
    user=users.find_one({"email":email},{'_id':0})
    if not user:
        return "email does not exist",None
    if verify_password(user["password"],password):
        user.pop("password")
        return "user is correct",user
    else:
        return "wrong password",None
def update_MySchedule(db,email,schedule):
    users=db["users"]
    print(email)
    users.update_one({"email":email},{"$set":{"mySchedule":schedule}})
    print(users.find_one({"email":email}))
def getUserAttribute(db,email,attribute):
    users=db["users"]
    user=users.find_one({"email":email},{'_id':0})
    return user[attribute]
def updateUser(db,user):
    if "name" not in user or 'email' not in user or "phoneNumber" not in user or "role" not in user:
        return {"error": "Missing 'data' parameter"}, 400
    if not re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user["email"]):
        return {"error": "Invalid email"}, 400
    if len(user["phoneNumber"]) != 8:
        return {"error": "Invalid phoneNumber"}, 400
    if not re.match(r"^[a-zA-Z\s'-]+$", user["name"]):
        return {"error": "Invalid name"}, 400
    users=db["users"]
    oldUser=users.find_one({"email":user["email"]})
    if not oldUser:
        return {"error": "Email does not exist"}, 400
    if oldUser["role"]=="admin"!=user["role"]:
        return {"error": "You can't change the role of an admin"}, 400
    users.update_one({"email":user["email"]},{"$set":{"name":user["name"],"phoneNumber":user["phoneNumber"],"role":user["role"]}})

    return {"success":"successfully updated"},200
def deleteUser(db,email):
    users=db["users"]
    try:
        users.delete_one({"email":email})
        return "deleted successfully",200
    except:
        return  "Email does not exist",400
def nb_user(db):
    users=db["users"]
    return users.count_documents({})

def exists(table,attribute,value):
    row=table.find_one({attribute: value})
    if row:
        return True
    else:
        return False
def readData(db,path):
    execls = path
    db["schedules"].drop()
    teachers=db["teachers_list"]
    classes=db["classes_list"]
    rooms=db["rooms_list"]
    for file in os.listdir(execls):
        df = pd.read_excel(execls + file, header=None)
    df = df.values
    data = []
    for i in range(2, len(df), 3):
        for j in range(1, len(df[i])):
            if j % 7 == 0:
                continue
            if df[i + 1][j] is np.nan or df[i][j] is np.nan:
                continue
            case = {}
            case["room"] = df[i][0]
            case["day"] = df[0][((j // 7) * 7) + 1]
            case["class"] = df[i][j]
            if case["class"].find("|")!=-1:
                case["time"] = case["class"][case["class"].index("|") + 1:]
                case["class"] = case["class"][:case["class"].index("|")]
            else:
                case["time"] = df[1][j]
            case["teacher"] = df[i + 1][j]
            case["subject"] = df[i + 2][j]
            if not teachers.find_one({"name":case["teacher"]}):
                return "teacher '"+case["teacher"]+"' does not exist",400
            if not classes.find_one({"name":case["class"]}):
                return "class '"+case["class"]+"' does not exist",400
            if not rooms.find_one({"name":case["room"]}):
                return "room '"+case["room"]+"' does not exist",400
            data.append(case)
    db["classes_schedule"].drop()
    t_schedule=db["classes_schedule"]
    data=readData()
    collection=db["classes_list"]
    times={"Lundi":[""],"Mardi":[""],"Mercredi":[""],"Jeudi":[""],"Vendredi":[""],"Samedi":[""]}
    all={}
    for i in collection:
        all[i]=copy.deepcopy(times)
    for i in data:
        t=False
        for j in collection:
            if i["class"] in j or j in i["class"] :
                t=True
                break
        if t:
            all[j][i["day"]].append(i["time"])

    for key,value in all.items():
        print(key,value)
        t_schedule.insert_one({"name":key,"schedule":value})
    db["schedules"].insert_many(data)
    print(db["schedules"])
    print("read data completed")
    return "completed",200
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
def times_overlap(time1, time2):
    def parse_time_range(time_range):
        start, end = time_range.split(" - ")
        return tuple(map(lambda t: int(t.split(":")[0]) * 60 + int(t.split(":")[1]), (start, end)))

    start1, end1 = parse_time_range(time1)
    start2, end2 = parse_time_range(time2)

    return max(start1, start2) < min(end1, end2)
def time_config(time):
    start,end=time.split(" - ")
    hs,ms=start.split(":")
    he,me=end.split(":")
    if len(hs)!=2:
        hs="0"+hs
    if len(ms)!=2:
        ms=ms+"0"
    if len(he)!=2:
        he="0"+he
    if len(me)!=2:
        me=me+"0"
    t=hs+":"+ms+" - "+he+":"+me
    return t


# reset Password
def initiate_password_reset(db, email):
    users = db["users"]
    user = users.find_one({"email": email})
    if not user:
        return False, "Email does not exist"
    
    # Generate a random reset token
    reset_token = os.urandom(16).hex()
    expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    
    # Store the reset token and its expiry time
    users.update_one(
        {"email": email},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expiry": expiry_time
        }}
    )
    return True, reset_token

def reset_password_with_token(db, token, new_password):
    users = db["users"]
    user = users.find_one({
        "reset_token": token,
        "reset_token_expiry": {"$gt": datetime.datetime.now()}
    })
    if not user:
        return False, "Invalid or expired reset token"
    hashed_password = hash_password(new_password)
    users.update_one(
        {"reset_token": token},
        {
            "$set": {"password": hashed_password},
            "$unset": {"reset_token": "", "reset_token_expiry": ""}
        }
    )
    return True, "Password reset successful"

def get_users_by_schedule(db, schedule_name):
    """Get users who should be notified about this schedule"""
    # Get all users
    all_users = users_list(db)
    users_to_notify = []
    if schedule_name == 'All':
        for user in all_users:
            users_to_notify.append(user)
    else :
        for user in all_users:
            # Check if this is their selected schedule
            if "mySchedule" in user and user["mySchedule"] == schedule_name:
                users_to_notify.append(user)
                continue
    
    return users_to_notify