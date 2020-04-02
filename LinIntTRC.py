import pandas as pd
import numpy as np
from sqlalchemy import create_engine
# treasury rate data from U.S. DEPARTMENT OF THE TREASURY
data1 = pd.read_excel(r'C:\Users\严书航\Desktop\Treasury yield curve2.xlsx')

data1.drop(columns=['Index', '1 Mo', '2 Mo'], inplace=True)

data1 = data1.interpolate()  # fill the Nan by interpolation

tyc_date = list(data1.columns[1:])
data1[tyc_date] = data1[tyc_date].applymap(lambda x: x/100)


# transpose the string date to float (year)
tyc_year = []
for x in tyc_date:
    s = x.split()
    if s[1] == 'Mo':
        tyc_year.append(int(s[0])/12)
    else:
        tyc_year.append(int(s[0]))


# using interpolation to find t-bill rates of all intervals (quarter)
# function to calculate the discount factor curve
def discount_factor(curve, date=tyc_year):
    ltcy = []
    for i in range(120):
        i = (i+1)/4
        for j in range(len(date)):
            if (i >= date[j]) & (i <= date[j+1]):
                ltcy.append(curve[j]+(curve[j+1]-curve[j])*(i-date[j])/(date[j+1]-date[j]))
                break
    discount = []
    for i in range(len(ltcy)):
        year = (i+1)/4
        if i < 4:
            discount.append(1/(1+ltcy[i]*year))
        else:
            discount.append(1/np.power((1+ltcy[i]), year))
    return discount


data2 = list(data1[tyc_date].apply(discount_factor, axis=1))
data2 = pd.DataFrame(data2)
data2['Date'] = data1['Date']
# data2.to_excel(r'C:\Users\严书航\Desktop\Discount Factors.xlsx')


selected_data = pd.read_excel(r'C:\Users\严书航\Desktop\data.xlsx')
# Required_data = selected_data.groupby(by='Date').count()
date = selected_data['Date'].unique()
date = pd.Series(date, name='Date').sort_values(ascending=False)

data3 = pd.merge(date, data2, how='left', on='Date')

data3 = data3.interpolate()

# data3.to_excel(r'C:\Users\严书航\Desktop\Discount Factors2.xlsx')
con = create_engine('mysql+mysqldb://root:1029@localhost/test', echo=False)
data3.to_sql('discount', con=con)




