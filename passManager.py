
import telebot,time,os,pyotp,mysql.connector,sys
from cryptography.fernet import Fernet
from datetime import datetime
from config import DB_CONFIG
import ctypes
if hasattr(sys, 'frozen'):
    # Running as compiled executable
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # Set the icon for the executable
    #icon_path = os.path.join(sys._MEIPASS, 'playback.ico')
    icon_path=r'B:\Projects\Python\pass\pass.ico'
    ctypes.windll.kernel32.SetConsoleIcon(ctypes.windll.user32.LoadImageW(0, icon_path, 1, 0, 0, 0x00000002))

BOT_TOKEN="6536427361:AAFxMGQpo8ZUvDx_WzgXxBhnKKEq2ls4UPk"
bot = telebot.TeleBot(BOT_TOKEN)
key = bytes(os.environ.get('SECRET'), 'utf-8')
cipher_suite = Fernet(key)

def log_message_response(msg, response):
    # Get the current date and time
    current_datetime = datetime.now().strftime('%H:%M:%S-%d/%m/%Y')
    
    # Format the log entry
    log_entry = f"{current_datetime} | {msg} | {response}\n"
    
    # Specify the file path
    log_file_path = r'B:\logs\passManager.txt'
    
    try:
        # Append the log entry to the file
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_entry)
        print("Log entry added successfully.")
    except Exception as e:
        print(f"Error: {str(e)}")
    
def verify(otp):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM t_otp')
    user = cursor.fetchall()[0]
    print(user)
    secret_key = user[1]
    print(secret_key)
    if secret_key:
        totp = pyotp.TOTP(secret_key)
        if totp.verify(otp):
            return "auth_success"
    return "WRONG OPT !"

def get_credentials(app):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = "SELECT login, password FROM t_pass WHERE app = %s"
        cursor.execute(query, (app,))
        credentials = cursor.fetchone()
        if credentials:
            login, encrypted_password = credentials
            decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
            return login, decrypted_password
        else:
            return None, "App not found in the database."
    except Exception as e:
        print("Error:", e)
        return None, "An error occurred while retrieving the credentials."

    finally:
        cursor.close()
        connection.close()

@bot.message_handler(commands=['pass'])
def send_message(message):
    command, *args = message.text.split(maxsplit=2)
    if len(args) < 2:
        log_message_response(message.text, "Missing data")
        bot.reply_to(message, "Missing data")
    else:
        app,otp = args[:2]
        ver=verify(otp)
        if(ver=="auth_success"):
            login, password = get_credentials(app)
            if login is not None:
                log_message_response(message.text, "Credentials sent success")
                response = f"Login: {login}\nPassword: {password}"
            else:
                response = password
                log_message_response(message.text, response)
            sent_message =bot.send_message(message.chat.id, response)
            
            time.sleep(5)
            bot.delete_message(message.chat.id, sent_message.message_id)
        else:
            time.sleep(3)
            log_message_response(message.text, ver)
            bot.send_message(message.chat.id,ver)




@bot.message_handler(commands=['setpass'])
def send_message(message):
    command, *args = message.text.split(maxsplit=3)
    if len(args) < 3:
        log_message_response(message.text, "Missing data")
        bot.send_message(message.chat.id, "/setpass appname login password")
    else:
        app_name, login,password = args[:3]
        encrypted_password = cipher_suite.encrypt(password.encode())

        # Store the data in the database
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            insert_query = "INSERT INTO t_pass (app, login, password) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (app_name, login, encrypted_password))
            conn.commit()
            cursor.close()
            conn.close()
            print("Data stored successfully.")
        except Exception as e:
            print(f"Error: {e}")
        log_message_response(message.text, f"Pass saved for {login}:{app_name}")
        bot.send_message(message.chat.id, f"Pass saved for {app_name}")



bot.infinity_polling()




