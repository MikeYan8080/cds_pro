import pandas as pd
from datetime import datetime as dt
from sqlalchemy import create_engine

start = dt.now()
# connect to mysql  database
engine = create_engine('mysql+mysqldb://root:1029@localhost/test', echo=False)

# data4 = pd.read_csv(r'C:\Users\严书航\Desktop\data2.csv', index_col=0)
# input the spread data
data4 = pd.read_sql_table(table_name='spread', con=engine)
# discount = pd.read_excel(r'C:\Users\严书航\Desktop\Discount Factors2.xlsx', index_col=0)
# input discount rate
discount = pd.read_sql_table(table_name='discount', con=engine)

# data4['Date'] = data4['Date'].map(lambda x: pd.to_datetime(x))
data5 = pd.merge(data4, discount, how='left', on='Date')
data5.drop(columns=['index', 'Index'], inplace=True)

data5.to_sql(name='combine', con=engine, if_exists='replace')

data5.info()

print('Cost:', dt.now()-start)