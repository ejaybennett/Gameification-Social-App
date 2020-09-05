from WebFramework import DB_NAME, PROFILE_TABLE_NAME, MESSAGES_TABLE_NAME
import WebFramework
import requests
import sqlite3
url = 'http://127.0.0.1:5000/'
connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()
test_user_username = 'test_boi'
test_user_password = 'mc_testy_face'
def test_create_profile():
    new_profile = {'username':test_user_username,
                   'password':test_user_password}
    r = requests.get(url+'/create_profile',params = new_profile).text
    command = """SELECT * FROM {} WHERE username = '{}'"""\
              .format(PROFILE_TABLE_NAME,'test_boi')
    cursor.execute(command)
    profile = cursor.fetchone()
    print(profile)

def test_update_profile():
    new_profile = {'username':test_user_username,
                   'password':test_user_password,'bio':'hoe ass bishhh'}
    r = requests.get(url+'/update_profile',params = new_profile).text
    command = """SELECT * FROM {} WHERE username = '{}'"""\
              .format(PROFILE_TABLE_NAME,'test_boi')
    cursor.execute(command)
    profile = cursor.fetchone()
    print(profile)

def test_public_profile():
    new_profile = {'username':test_user_username}
    r = requests.get(url+'/public_profile',params = new_profile).text
    print(r)

def test_private_profile():
    new_profile = {'username':test_user_username,'password':test_user_password}
    r = requests.get(url+'/public_profile',params = new_profile).text
    print(r)


if __name__ == '__main__':
    tests = [ test_create_profile,test_update_profile,
              test_public_profile,test_private_profile]
    for test in tests:
        test()

