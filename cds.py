import pandas as pd
import numpy as np
from scipy.optimize import fsolve
from matplotlib import pyplot as plt

# treasury rate data from U.S. DEPARTMENT OF THE TREASURY website
treasury_yield_curve = [0.79, 0.64, 0.45, 0.41, 0.39, 0.49, 0.53, 0.58, 0.69, 0.74, 1.09, 1.25]
treasury_yield_curve = [x/100 for x in treasury_yield_curve]
tyc_date = ['1 Mo',	'2 Mo', '3 Mo',	'6 Mo', '1 Yr',	'2 Yr',	'3 Yr',	'5 Yr',	'7 Yr',	'10 Yr', '20 Yr', '30 Yr']

# transpose the string date to float (year)
tyc_year = []
for x in tyc_date:
    s = x.split()
    if s[1] == 'Mo':
        tyc_year.append(int(s[0])/12)
    else:
        tyc_year.append(int(s[0]))


# using interpolation to find t-bill rates of all intervals (quarter)
def linear_tcy(curve, date):
    ltcy = []
    for i in range(120):
        i = (i+1)/4
        for j in range(len(date)):
            if (i >= date[j]) & (i <= date[j+1]):
                ltcy.append(curve[j]+(curve[j+1]-curve[j])*(i-date[j])/(date[j+1]-date[j]))
                break
    return ltcy


# the yield curve (quarterly)
ltcy = linear_tcy(treasury_yield_curve,tyc_year)


# function to calculate the discount factor curve
def discout_factor(ltcy):
    discount = []
    for i in range(len(ltcy)):
        year = (i+1)/4
        if i < 4:
            discount.append(1/(1+ltcy[i]*year))
        else:
            discount.append(1/np.power((1+ltcy[i]), year))
    return discount


df = discout_factor(ltcy)


# tyc = pd.DataFrame({'yield': treasury_yield_curve, 'date': tyc_date})
# tyc.set_index(tyc.date, inplace=True)
# tyc.drop(columns='date', inplace=True)


# input the csd data

# credit_default_spread = [0.40,	0.56, 0.76,	0.97, 1.03,	1.10, 1.16,	1.34, 1.36,	1.38]
# cds_rate = [x/100 for x in credit_default_spread]
# cds_date = ['Spread1y',	'Spread2y',	'Spread3y',	'Spread4y',	'Spread5y',	'Spread7y',	'Spread10y',
#             'Spread15y', 'Spread20y', 'Spread30y']
# cds_year = [int(x[6:-1]) for x in cds_date]

credit_default_spread = [100, 110, 120, 140, 150, 160, 165]
cds_rate = [x/10000 for x in credit_default_spread]

cds_year = [0.5, 1, 2, 3, 5, 7, 10]

recover = 0.4


# the survival probability function, input the hazard rate and the time(quarter),
# it will return the survival probability. It's a recursive function. Time-cost but simple.
def Q(lam, quarter):

    if quarter == 0:
        return 1
    if quarter == 1:
        return np.exp(-1/4 * lam[0])

    year = quarter/4
    if year <= cds_year[0]:
        multiplier = np.exp(-1/4 * lam[0])
    else:
        for x in range(len(cds_year)):
            if (year > cds_year[x]) & (year <= cds_year[x+1]):

                multiplier = np.exp(-1 / 4 * lam[x+1])
                break
    sur_pro = Q(lam, quarter-1)*multiplier
    return sur_pro


lamm = np.zeros(len(cds_year))

# use a loop to calculate every hazard rate.
for x in range(len(cds_year)):
    year = cds_year[x]
    quarter = int(year*4)

# build a function show the difference between premium leg and protection leg
    def func(y):
        lamm[x] = y
        sum = 0
        for i in range(quarter):
            sum += (cds_rate[x]/4*Q(lamm, i+1) - (1 - recover)*(Q(lamm, i) - Q(lamm, i+1)))*df[i]
        return sum
# use fsolve function to solve the hazard rate
    r = fsolve(func, 0)
    lamm[x] = r

output = pd.DataFrame({'Year': cds_year, 'Risk Intensity': lamm, 'Spread': credit_default_spread})
print(output)

plt.step(cds_year, lamm)
plt.show()