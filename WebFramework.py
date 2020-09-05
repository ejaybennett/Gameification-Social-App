from flask import Flask, request, render_template, send_file
import sqlite3
import smtplib
import random
import string
from binascii import a2b_base64
import os
##Universal Variables
DB_NAME = "C:/Users/ejayb/Socialite/backend/profiles.db"
PROFILE_TABLE_NAME = 'profiles'
MESSAGES_TABLE_NAME = 'messages'
FIELDS = ['privateID', 
    'username',
    'password',
    'email',
    'phone_number',
    'first_name',
    'last_name',
    'gender',
    'bio',
    'hobbies' ,
    'photos',
    'contacts']
TYPES = {'privateID':'VARCHAR(10)',
    'username':'VARCHAR(40)',
    'password':'VARCHAR(40)',
    'email':'VARCHAR(40)',
    'phone_number':'VARCHAR(40)',
    'first_name':'VARCHAR(40)',
    'last_name':'VARCHAR(40)',
    'gender':'VARCHAR(10)',
    'bio':'VARCHAR(400)',
    'hobbies':'VARCHAR(40)',
    'photos':'VARCHAR(40)',
    'contacts':'VARCHAR(1000)'}
PUBLIC_FIELDS = [
    'username',
    'first_name',
    'last_name',
    'bio',
    'hobbies' ,
    'photos',
    'gender']
CARD_FIELDS = [
    'username',
    'first_name',
    'last_name',
    'bio',
    'hobbies' ,
    'photos',
    'gender']
MESSAGE_FIELDS = ['user1', 'user2','can_message','user_1_like','user_2_like','message_file_name']
MESSAGES_DIRECTORY = ''

def get_connection():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    return cursor, connection

def get_rand_ID(stringLength = 10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def initialize_database():
    cursor, connection = get_connection()
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    sql_command = "CREATE TABLE "+PROFILE_TABLE_NAME+' (' +\
                  ','.join([field + ' ' + TYPES[field] for field in FIELDS])\
    +');'
    print(sql_command)
    cursor.execute(sql_command)
    connection.commit()

def print_table_contents(table):
    cursor, connection = get_connection()
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    sql_command = """
    SELECT * FROM {}""".format(table)
    cursor.execute(sql_command)
    print(cursor.fetchall())


class Profile:
    def __init__(self):
        cursor, connection = get_connection()
        self.set_fields = []
    def username_password_correct(self):
        cursor, connection = get_connection()
        assert 'username' in self.set_fields
        command = """ SELECT * FROM {}
        WHERE username = '{}'""".format(PROFILE_TABLE_NAME, self.username)
        cursor.execute(command)
        result = cursor.fetchone()
        if result is None or len(result)==0:
            return False
        return True
    
    def user_exists(self):
        cursor, connection = get_connection()
        assert 'username' in self.set_fields
        command = """ SELECT * FROM {}
        WHERE username = '{}'""".format(PROFILE_TABLE_NAME, self.username)
        cursor.execute(command)
        result = cursor.fetchone()
        if result is None or len(result)==0:
            return False
        return True
    
    def populate_from_db_private(self):
        cursor, connection = get_connection()
        assert self.username_password_correct()
        command = """ SELECT * FROM {}
        WHERE username = '{}' AND password = '{}'""".format(PROFILE_TABLE_NAME, self.username, self.password)
        cursor.execute(command)
        connection.commit()
        for (field, value) in zip(FIELDS, cursor.fetchone()):
            setattr(self, field,value)
            self.set_fields.append(field)
        self.set_fields = list(set(self.set_fields))

    def populate_from_db_public(self):
        cursor, connection = get_connection()
        assert self.user_exists()
        command = """ SELECT """+','.join([f for f in PUBLIC_FIELDS])+"""
FROM {} WHERE username = '{}' """.format(PROFILE_TABLE_NAME, self.username)
        print(command)
        cursor.execute(command)
        connection.commit()
        for (field, value) in zip(PUBLIC_FIELDS, cursor.fetchone()):
            setattr(self, field,value)
            self.set_fields.append(field)
        self.set_fields = list(set(self.set_fields))
    
    def populate_from_request(self,request):
        cursor, connection = get_connection()
        request_fields = list(request.args.keys())
        print(request_fields)
        if 'username' not in request_fields:
            raise ValueError('No username or password given')
        for field in request_fields:
            setattr(self, field,request.args[field])
            self.set_fields.append(field)
        self.set_fields = list(set(self.set_fields))

    def write_to_db(self):
        cursor, connection = get_connection()
        if self.user_exists():
            command = """UPDATE {} SET {} WHERE username = '{}' AND password = '{}' """\
                  .format(PROFILE_TABLE_NAME,', '.join([ "{} = '{}'".format( field, str(getattr(self,field))) for field in self.set_fields])
                                                                                , self.username,self.password)
        else:
            self.privateID = get_rand_ID
            self.set_fields.append('privateID')
            command = """INSERT INTO {} ({}) VALUES ({})"""\
                  .format(PROFILE_TABLE_NAME, ','.join(self.set_fields),','.join(["'"+str(getattr(self,field))+"'" for field in self.set_fields]))
        print(command)
        cursor.execute(command)
        connection.commit()

    def to_string(self):
        return ', '.join([field + ': ' + str(getattr(self,field)) for field in self.set_fields])


app = Flask(__name__)


@app.route('/private_profile',methods=['GET'])
def serve_private_profile():
    profile = Profile()
    profile.populate_from_request(request)
    profile.populate_from_db_private()
    return profile.to_string()

@app.route('/create_profile',methods=['GET'])
def create_profile():
    profile = Profile()
    profile.populate_from_request(request)
    if not(profile.user_exists()):
        profile.write_to_db()
        return profile.to_string()
    else:
        return 'user already exists!'

@app.route('/public_profile',methods=['GET'])
def serve_public_profile():
    profile = Profile()
    profile.populate_from_request(request)
    profile.populate_from_db_public()
    return profile.to_string()
@app.route('/update_profile',methods=['GET'])
def update_profile():
    profile = Profile()
    profile.populate_from_request(request)
    if profile.username_password_correct():
        profile.write_to_db()
        return profile.to_string()
    else:
        return 'Failed to update profile'

def run():
    if not(os.path.exists(DB_NAME)):
        initialize_database()
    app.run()

if __name__ == "__main__":
    run()
