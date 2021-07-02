from pandas import ExcelWriter
from datetime import date
import os.path
from pathlib import Path
# from scripts import screenModule_finnhub
from scripts import screenModule
from scripts import send_mail

if __name__ == '__main__':

    testing = False
    testing = True

    # index_array = ['hsi','dow','sp500','nasdaq']
    index_array = ['dow']

    today = date.today()
    today_date = today.strftime("%Y%m%d")
    Path(f"output").mkdir(parents=True, exist_ok=True)
    writer = ExcelWriter(f"output/ScreenOutput_{today_date}_test.xlsx")

    screenModule.remove_dir()

    temp = {}
    for value in index_array:
        temp[value] = screenModule.screen(value, testing)

    for value in index_array:
        temp[value].to_excel(writer, sheet_name = value)

    writer.save()
    # writer.close()

    send_mail.send(today_date, testing);
