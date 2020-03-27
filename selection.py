import pandas as pd
import numpy as np
from datetime import datetime as dt
from sqlalchemy import create_engine
import os
start = dt.now()
files_name = os.listdir(r'C:\Users\严书航\Desktop\CDSCOMP')
# ticker_selected = ['SVU', 'S', 'RRD', 'GT', 'NRG', 'FTR', 'X', 'GNW', 'THC', 'CHK', 'BBY', 'CVC', 'DF', 'SLM', 'AMD',
#                    'WIN', 'HRB', 'ANR', 'JCP', 'PHM', 'PBI', 'MS', 'BTU', 'AES', 'OI']
# select 26 companies
ticker_selected = ['SVU', 'GT', 'X', 'THC', 'CHK', 'BBY', 'CVC', 'AMD', 'HRB', 'JCP', 'PBI', 'AES', 'OI',
                   'MSFT', 'JNJ', 'JPM', 'PG', 'UNH', 'T', 'HD', 'KO', 'INTC', 'DIS', 'PEP', 'PFE', 'XOM']


selected_data = pd.DataFrame({}, columns=['Date', 'Ticker', 'DocClause', 'Spread6m', 'Spread1y', 'Spread2y',
                                            'Spread3y', 'Spread4y', 'Spread5y','Spread7y', 'Spread10y', 'Spread15y',
                                            'Spread20y', 'Spread30y', 'Recovery', 'CompositeLevelRecovery'])
count = 1
for name in files_name:
    openname = 'C:\\Users\\严书航\\Desktop\\CDSCOMP\\' + name
    data = pd.read_csv(openname, skiprows=2)
    # conditions for selection
    condition1 = [x in ticker_selected for x in data['Ticker']]
    condition2 = data['DocClause'] == 'XR14'
    condition3 = data['Ccy'] == 'USD'
    data1 = data[condition1 & condition2 & condition3]

    data2 = data1[['Date', 'Ticker', 'DocClause', 'Spread6m', 'Spread1y', 'Spread2y', 'Spread3y', 'Spread4y', 'Spread5y',
                  'Spread7y', 'Spread10y', 'Spread15y', 'Spread20y', 'Spread30y', 'Recovery', 'CompositeLevelRecovery']]

    selected_data = selected_data.append(data2, ignore_index=True)
    print(count)
    count += 1
    # if count == 10:
    #     break


selected_data['Date'] = pd.to_datetime(selected_data['Date'])
selected_data.sort_values(by=['Date', 'Ticker'], ascending=[False, True], inplace=True, ignore_index=True)


condition11 = pd.notna(selected_data['Spread1y'])
condition12 = pd.notna(selected_data['Spread2y'])
condition13 = pd.notna(selected_data['Spread5y'])
condition14 = pd.notna(selected_data['Recovery'])
condition4 = condition11 & condition12 & condition13 & condition14

comp_data = selected_data[condition4]

years_of_spread =['Spread6m', 'Spread1y', 'Spread2y','Spread3y', 'Spread4y', 'Spread5y',
                  'Spread7y', 'Spread10y', 'Spread15y','Spread20y', 'Spread30y','Recovery']


def formatad(x):
    if pd.isna(x):
        return None
    return np.round(np.float(x[0:-1])/100, 5)


pd.set_option('mode.chained_assignment', None)
comp_data[years_of_spread] = comp_data[years_of_spread].applymap(formatad)
comp_data.reset_index(inplace=True, drop=True)

# comp_data.to_csv(r'C:\Users\严书航\Desktop\data2.csv')

engine = create_engine('mysql+mysqldb://root:1029@localhost/test', echo=False)
comp_data.to_sql(name='spread', con=engine, if_exists='replace')

comp_data.info()
print('Cost', dt.now()-start)