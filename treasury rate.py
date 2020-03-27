import pandas as pd

data0 = pd.read_excel(r'C:\Users\严书航\Desktop\Treasury yield curve.xlsx')


def adjustdata(x):
    if type(x) == str:
        return x
    month = x.year - 2000
    day = x.month
    year = x.day
    date = '{}/{}/{}'.format(month, day, year)
    return date


data0['Date'] = data0['Date'].apply(adjustdata)
data0['Date'] = pd.to_datetime(data0['Date'])

# print(data0)
# print(data0.info())

data0.to_excel(r'C:\Users\严书航\Desktop\Treasury yield curve2.xlsx')