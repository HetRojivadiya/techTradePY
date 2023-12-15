import pandas as pd
import numpy as np
from tradingview_ta import TA_Handler, Interval
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
import threading
import time

app = Flask(__name__)
env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

firebase_cred = {
   "type": "service_account",
  "project_id": "tech-t-2473d",
  "private_key_id": "488f431a1bf31d0943306c561a91971692adcda6",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC1PEQccbgMA4wS\nN/Ko5bRVJhbfLnVXyqCgTLqlqbv3wjPFLpZ1SPKhfA5uRHHFMelw/JoV/IyQc5Io\nnWCCphqkG3SSZcEo6/8ePjHwmOUB8474vPg4l8m3RnVQ832aFyyP0I5rfny2tKXd\nlqOT86VfKRcnrW6+3zq2SoFGjj2F3sy7d9euGj3B9pbznEv3Q8HVl4XkCmoHJUoa\nKMIrXfS79R1MK9f9RM+Phnd4Dm6v7SdX2AC/wWBOY4+ZqRenW+z9iBpX7oN/WMHn\nMPsyuT+6CVuOcYMQrhYQQ57VZAPZXMdj9fF1JcOKo6WYIFTczgEgsosgeNVFlH7T\nLKZMYIIdAgMBAAECggEARwFsHArP1WEkZVTnLRYF/6BTMLCmh7VbFkLJk7M68jhz\niQsWJrBkYzFUBA6r1lsWP06wXfHa7pNhDamPENDcOjSJiPv14D8J7oLmlQGKI6gV\neU2sIJwTi0s/Fm63ZII00smequ3dFcYUAAuPXh2EypIyQLjZ3U1fVuE84fRDlWlK\nwO0nYNJO874JQ+vZxdSR1o3M9MvaMucprZXH093ioOuX6nQlPveRDEnFSAbDnjh1\npTcleerbRFtZ7pJEqy7iIOc3CKaI2KI+0pXmuTzetASs5C0/JUXx/TNG2FSSpkKj\n6yQnZQiFm6pIBFFMDoc0Ufiu3lf47BN2ipo3tbIPPwKBgQDfITf4Rx7j5X1HBcrT\nnH7OdH6Q3v+UJL1ZDztuy7DML6qNBS6zUlb0o6O4VqqGY73zvekkXXPyEDM4BBHD\ndI55r/BfxQVrh80snCA8jWdUP+r98btw/KgL2y+WYltgSeRbMYSXTpARpTzKjMCw\nH0mOxRYfdpVoZRCZ6R/LWY+jJwKBgQDP7xtajzrNvUwShJYnyyKYHFyLh2omlKjk\nRLRuezO3YhSG1cWEeGRbHB0JZoh/IxJLVq+jTId5r8SrxgY+u6sD418mBOYygs7k\neSpYWZ7KbAMRcjycQAf7QCXDuofp7URoAwD6Q/AX5kAW9FRPA2LPCgURxuc8eyyY\nCdANyE9rGwKBgQCBJssszI3Wv8jpyTKDlfvYKJnx5QHuj+2BlU2DbidhqN2BTtSf\nOzPV2rozQwblTupuISjHwcgQ/suGyuQ1TEwDp5Ds/i+K9EoQXjZSlk6O94hfgQJL\n/hKO+knrM/dMHrktB9aFdhXyAMDVRO9rglCjcPTDNXJ5wLYBQG0E2UxI1QKBgQC3\nUqPXL7g0c9SB7wtDgkC5wyeEjJr18NMGjdxWG6D46SwXxJkjtdEk0qB3DUMCdDVI\n3uBzJKG8k07d8vTGkkawYuIcbu1VUyZ9IKZIxprM9HWwB/uP9pQS2/dvnSD/CQTq\nftt5yjP/niybEEbUcrPGvZrClY6BMEecs+oOfLAoSQKBgENE3rNGmJSkqqOkg439\nRVSiNWdfDoOD4XUE1Odvv5vXPnRZkblWTFpeSorM4oCnABWphK40/CjdvyU0GBng\n3vam7tsLIoem/sUh/auXNWo9PAFlkgHxNaouBP4oWEZMvLtI6VZlyTbVenGooMC9\nbIL/NlYDwjVuBwUmvsKXmcU2\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-h13gu@tech-t-2473d.iam.gserviceaccount.com",
  "client_id": "101005758955804568286",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-h13gu%40tech-t-2473d.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_cred)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def update_data():
    symbols = [
            "NIFTY", "COALINDIA", "SBIN", "NTPC", "ADANIENT", "BAJAJ_AUTO",
            "INFY", "APOLLOHOSP", "RELIANCE", "EICHERMOT", "HCLTECH", "HDFCLIFE",
            "AXISBANK", "NESTLEIND", "TATAMOTORS", "WIPRO", "ADANIPORTS", "MARUTI",
            "M_M", "POWERGRID", "ONGC", "GRASIM", "TATASTEEL", "BHARTIARTL",
            "SUNPHARMA", "LT", "INDUSINDBK", "HDFCBANK", "LTIM", "SBILIFE",
            "TATACONSUM", "BAJFINANCE", "CIPLA", "HINDALCO", "ICICIBANK", "TECHM",
            "BPCL", "HEROMOTOCO", "ASIANPAINT", "TITAN", "BRITANNIA", "DIVISLAB",
            "TCS", "ULTRACEMCO", "UPL", "BAJAJFINSV", "JSWSTEEL", "KOTAKBANK",
            "ITC", "HINDUNILVR", "DRREDDY"
    ]

    above_ema20 = []  # for ema
    below_ema20 = []
    above_ema50 = []
    below_ema50 = []
    above_ema100 = []
    below_ema100 = []
    above_ema200 = []
    below_ema200 = []

    above_60 = []  # for rsi
    below_40 = []
    between = []
        
    positive = []  # for macd
    negative = []


    for symbol in symbols:
            output = TA_Handler(symbol=symbol,
                                screener='India',
                                exchange='NSE',
                                interval=Interval.INTERVAL_1_DAY)

            indi = output.get_analysis().indicators # get indicators

            ema20 =  round(indi['EMA20'], 2)  # macd ----------
            ema50 =  round(indi['EMA50'], 2)
            ema100 =  round(indi['EMA100'], 2)
            ema200 =  round(indi['EMA200'], 2)
            op = round(indi['open'], 2)
            
            rsi = round(indi['RSI'], 2) # rsi ----------
            
            macd = round((indi['MACD.macd'] - indi['MACD.signal']) , 2)  # macd ----------
            
            
            print(f"{symbol} :")
            print(f"RSI : {rsi}")
            print(f"EMA ->  EMA20 : {ema20}   EMA50:{ema50}   EMA100:{ema100}   EMA200:{ema200}")
            print(f"MACD : {macd}")
            print("-----------------------------------------")


        
    # conditions
    # ------------------------------------------------------------------------------------------------------------------------

            # --- conditions for ema ----
    # ema20  
            if op >= ema20 :
                above_ema20.append(f"{symbol} : {ema20}  ->  LTP : {op}")
            elif ema20 < op:
                below_ema20.append(f"{symbol} : {below_ema20}  ->  LTP : {op}")
    # ema50
            if op >= ema50 :
                above_ema50.append(f"{symbol} : {ema50}  ->  LTP : {op}")
            elif ema50 < op:
                below_ema50.append(f"{symbol} : {below_ema50}  ->  LTP : {op}")
    # ema100
            if op >= ema100 :
                above_ema100.append(f"{symbol} : {ema100}  ->  LTP : {op}")
            elif ema100 < op:
                below_ema100.append(f"{symbol} : {below_ema100}  ->  LTP : {op}")
    # ema200
            if op >= ema200 :
                above_ema200.append(f"{symbol} : {ema200}  ->  LTP : {op}")
            elif ema200 < op:
                below_ema200.append(f"{symbol} : {below_ema200}  ->  LTP : {op}")
        
        
            
            # ------ conditions for rsi -------
                
            if rsi >= 70 :
                above_60.append(f"{symbol} : {rsi}")
            elif rsi < 30:
                below_40.append(f"{symbol} : {rsi}")
            else:
                between.append(f"{symbol} : {rsi}")
        
        
            # --- conditions for macd ----
            if macd >= 0 :
                positive.append(f"{symbol} : {macd}")
            else:
                negative.append(f"{symbol} : {macd}")
    # -----------------------------------------------------------------------------------------------------------------------

        
        
    #     for replacement
    # --------------------------------------------------------------------------------------------------------------------------
            # ----------  replace ema  -------------------------------------
    def replace_ema( document_id, new_array1, new_array2,new_array3, new_array4,new_array5, new_array6,new_array7, new_array8):
            # Fetch the document
        doc_ref = db.collection('EMA').document(document_id)
        doc = doc_ref.get()

        if doc.exists:
                # Update the array field
            doc_ref.update({'above_ema20': new_array1})
            doc_ref.update({'below_ema20': new_array2}) #-----
            doc_ref.update({'above_ema50': new_array3})
            doc_ref.update({'below_ema50': new_array4}) #-----
            doc_ref.update({'above_ema100': new_array5})
            doc_ref.update({'below_ema100': new_array6}) #-----
            doc_ref.update({'above_ema200': new_array7})
            doc_ref.update({'below_ema200': new_array8}) #-----
            print(f"Array in document {document_id} replaced successfully.")
        else:
            print(f"Document {document_id} not found.")

    replace_ema('ema', above_ema20,below_ema20, above_ema50,below_ema50, above_ema100,below_ema100, above_ema200, below_ema200)

    print("ema replaced successfully")


            # ----------- replace rsi --------------------------------
    def replace_rsi(document_id, new_array1, new_array2, new_array3):
        # Fetch the document
        doc_ref = db.collection('RSI').document(document_id)
        doc = doc_ref.get()

        if doc.exists:
            # Update the array field
            doc_ref.update({'above_60': new_array1})
            doc_ref.update({'below_40': new_array2})
            doc_ref.update({'between': new_array3})
            print(f"Array in document {document_id} replaced successfully.")
        else:
            print(f"Document {document_id} not found.")


    replace_rsi('rsi', above_60, below_40, between)

    print("rsi replaced successfully")


            # ------------ replace macd ---------------------------
    def replace_macd( document_id, new_array1, new_array2):
        # Fetch the document
        doc_ref = db.collection('MACD').document(document_id)
        doc = doc_ref.get()

        if doc.exists:
            # Update the array field
            doc_ref.update({'positive': new_array1})
            doc_ref.update({'negative': new_array2})
            print(f"Array in document {document_id} replaced successfully.")
        else:
            print(f"Document {document_id} not found.")


    replace_macd( 'macd', positive, negative)
    print("macd replaced successfully")


    # --------------------------------------------------------------------------------------------------------------------------
    print("all set")

# Function to run update_data() every 3 minutes
def schedule_data_update():
    while True:
        update_data()
        time.sleep(180)  # 180 seconds = 3 minutes

# Route to trigger the update manually (optional)
@app.route('/update', methods=['GET'])
def trigger_update():
    update_data()
    return 'Data updated!'

if __name__ == '__main__':
    # Start a thread to run update_data() every 3 minutes
    update_thread = threading.Thread(target=schedule_data_update)
    update_thread.daemon = True
    update_thread.start()

    # Start Flask server
    app.run(debug=True)  # Set debug=False for production