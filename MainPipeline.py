# Testing 

import pandas as pd

dataF = pd.read_csv("pedwar_raw_sector_ticks(in).csv")
datatr = dataF['ts'].str.contains('/', na=False)

fullDates = pd.to_datetime(dataF.loc[datatr, 'ts']) 

truncDates = dataF.loc[~datatr, 'ts'] 


#truncts = dataF[~datatr].head(5).to_string()

partstr = truncDates.str.split(':')
minutestr = partstr.str[0].astype(int)
secondstr = partstr.str[1].astype(float)

transformDates = pd.to_datetime({
    'year': 2026, 
    'month': 2,
    'day': 12,
    'hour': 9,
    'minute': minutestr,
    'second': secondstr
})
print(fullDates)
print(transformDates)

dataF["timestamps"] = pd.NaT
dataF.loc[fullDates, "timestamps"] = fullDates
dataF.loc[transformDates, "timestamps"] = transformDates


sample = dataF[["ticker", "timestamps", "mid"]]
print(sample)
