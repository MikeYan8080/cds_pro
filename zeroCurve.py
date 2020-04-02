# similar to LinIntTRC, just change the data source from yield to zero curve

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# input the original zero curve
zdata = pd.read_csv('Quandl Zero Curve FED-SVENY.csv')
zdata['Date'] = pd.to_datetime(zdata['Date'])

# select the time we need
zdata1 = zdata[(zdata['Date'] <= pd.to_datetime('2018-12-31')) & (zdata['Date'] >= pd.to_datetime('2001-01-01'))]

# change from % to float
pd.set_option('mode.chained_assignment', None)
coname = list(zdata1.columns[1:])
zdata1[coname] = zdata1[coname].applymap(lambda x: x/100)
zyear = [int(x[-2:]) for x in coname]


# using interpolation to find t-bill rates of all intervals (quarter)
# function to calculate the discount factor curve
def discount_factor(curve, date=zyear):
    ltcy = []
    for i in range(120):
        i = (i+1)/4
        if i < 1:
            ltcy.append(i*curve[0])
        else:
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


# apply the funtion to every row to get the default factors
zdata2 = list(zdata1[coname].apply(discount_factor, axis=1))
zdata2 = pd.DataFrame(zdata2)
zdata1.reset_index(drop=True, inplace=True)
zdata2['Date'] = zdata1['Date']


engine = create_engine('mysql+mysqldb://root:1029@localhost/test', echo=False)
selected_data = pd.read_sql_table(table_name='spread', con=engine)

# Required_data = selected_data.groupby(by='Date').count()
date = selected_data['Date'].unique()
date = pd.Series(date, name='Date').sort_values(ascending=False)

zdata3 = pd.merge(date, zdata2, how='left', on='Date')

zdata3 = zdata3.interpolate()

zdata3.to_sql('zdiscount', con=engine)



