import pandas as pd
import numpy as np
from datetime import datetime as dt
from scipy.optimize import fsolve
from sqlalchemy import create_engine

start = dt.now()
# connect to mysql  database
engine = create_engine('mysql+mysqldb://root:1029@localhost/test', echo=False)

# data4 = pd.read_csv(r'C:\Users\严书航\Desktop\data2.csv', index_col=0)
# input the spread data
# data4 = pd.read_sql_table(table_name='spread', con=engine)
# # discount = pd.read_excel(r'C:\Users\严书航\Desktop\Discount Factors2.xlsx', index_col=0)
# # input discount rate
# discount = pd.read_sql_table(table_name='discount', con=engine)

years_of_spread =['Spread6m', 'Spread1y', 'Spread2y','Spread3y', 'Spread4y', 'Spread5y',
                  'Spread7y', 'Spread10y', 'Spread15y','Spread20y', 'Spread30y']

# data4 = data4[0:30]
# # data4['Date'] = data4['Date'].map(lambda x: pd.to_datetime(x))
# data5 = pd.merge(data4, discount, how='left', on='Date')
# data5.drop(columns=['index', 'Index'], inplace=True)
# data5[list(range(120))] = data5[list(range(120))] .applymap(lambda x: np.round(x, 3))
# data5.to_excel(r'C:\Users\严书航\Desktop\test2.xlsx')

data5 = pd.read_sql_table(table_name='zcombine', con=engine)
data5.drop(columns='index', inplace=True)

# data5 = data5[0:6540]  # 2018
# data5 = data5[6540:14332]  # 2017
# data5 = data5[14332:22011]  # 2016
# data5 = data5[22011:29594]  # 2015
# data5 = data5[29594:37234]  # 2014
# data5 = data5[37234:44725]  # 2013
# data5 = data5[44725:53375]  # 2012
# data5 = data5[53375:59855]  # 2011
# data5 = data5[59855:67629]  # 2010
# data5 = data5[67629:75182]  # 2009
# data5 = data5[75182:82364]  # 2008
# data5 = data5[82364:89817]  # 2007
# data5 = data5[89817:96655]  # 2006





def find_hazard(x):

    recover = x['Recovery']
    df = x[16:]
    # print(df)
    cds_date = x[years_of_spread].dropna()
    # print(cds_date)
    cds_rate = list(cds_date)
    cds_date = list(cds_date.index)
    if cds_date[0] == 'Spread6m':
        cds_year = [0.5] + [int(x[6:-1]) for x in cds_date[1:]]
    else:
        cds_year = [int(x[6:-1]) for x in cds_date]
    # print(cds_year)


    # the survival probability function, input the hazard rate and the time(quarter),
    # it will return the survival probability. It's a recursive function. Time-cost but simple.
    def Q(lam, quarter, cds_year=cds_year):

        if quarter == 0:
            return 1
        if quarter == 1:
            return np.exp(-1 / 4 * lam[0])

        year = quarter / 4
        if year <= cds_year[0]:
            multiplier = np.exp(-1 / 4 * lam[0])
        else:
            for x in range(len(cds_year)):
                if (year > cds_year[x]) & (year <= cds_year[x + 1]):
                    multiplier = np.exp(-1 / 4 * lam[x + 1])
                    break
        sur_pro = Q(lam, quarter - 1) * multiplier
        return sur_pro

    lamm = np.zeros(len(cds_year))

    # use a loop to calculate every hazard rate.
    for x in range(len(cds_year)):
        year = cds_year[x]
        quarter = int(year * 4)

        # build a function show the difference between premium leg and protection leg
        def func(y):
            lamm[x] = y
            sum = 0
            for i in range(quarter):
                sum += (cds_rate[x] / 4 * Q(lamm, i + 1) - (1 - recover) * (Q(lamm, i) - Q(lamm, i + 1))) * df[i]
            return sum

        # use fsolve function to solve the hazard rate
        r = fsolve(func, x0=0, xtol=0.00001, maxfev=1000)
        lamm[x] = r

    hazard_rate = pd.Series(lamm, index=cds_date)
    return hazard_rate


# every 20 rows input into the mysql
for n in range(360, len(data5), 20):
    data55 = data5[n-20:n]
    # data55.reset_index(inplace=True, drop=True)
    for i, x in data55.iterrows():
        if i == n-20:
            hazard_table = pd.Series(data=find_hazard(x), index=years_of_spread, dtype='float64')
            continue
        hazard_r = find_hazard(x)
        hazard_table = pd.concat([hazard_table, hazard_r], axis=1, ignore_index=True)
        print(i)


    data55 = data55[['Date', 'Ticker', 'DocClause', 'Recovery', 'CompositeLevelRecovery']]

    h = hazard_table.T
    h.set_index(data55.index, inplace=True)
    data6 = pd.concat([data55, h], axis=1)

    new_name = [x.replace('Spread', 'Risk Intensity ') for x in years_of_spread]
    change = dict(zip(years_of_spread, new_name))
    data6.rename(columns=change, inplace=True)


    # data6.to_csv(r'C:\Users\严书航\Desktop\hazard.csv')

    data6.to_sql(name='zhazard7', con=engine, if_exists='append')
# data6.info()

print('Cost ', dt.now() - start)


