import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqldb://root:1029@localhost/test', echo=False)

name = ['hazard{}'.format(x) for x in range(2005, 2019, 1)]

total_hazard = [pd.read_sql_table(table_name=y, con=engine, index_col='index') for y in name]

union = pd.concat(total_hazard, axis=0, ignore_index=True)
union.sort_values(by=['Date', 'Ticker'], ascending=[False, True], inplace=True, ignore_index=True)

union.to_sql(name='hazard01to18', con=engine, if_exists='replace')
union.info()