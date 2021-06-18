from pandas import ExcelWriter
from datetime import date
import os.path
from pathlib import Path

from scripts import screenModule_finnhub
# from scripts import screenModule
from scripts import send_mail

if __name__ == '__main__':
    # index_array = ['hsi','dow','sp500','nasdaq']
    index_array = ['hsi']
    
    today = date.today()
    d1 = today.strftime("%Y%m%d")
    Path(f"output").mkdir(parents=True, exist_ok=True)
    writer = ExcelWriter(f"output/ScreenOutput_{d1}_finnhub.xlsx")
    
    temp = {}
    
    for value in index_array:
        temp[value] = screenModule.screen(value)
        
    for value in index_array:
        temp[value].to_excel(writer, sheet_name = value)
    
    writer.save()
    # writer.close()
    
    # testing = True
    # send_mail.send(d1, testing);