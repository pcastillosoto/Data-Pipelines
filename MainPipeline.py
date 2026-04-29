
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

dataF = pd.read_csv("pedwar_raw_sector_ticks(in).csv")

dataTs = dataF['ts'].str.contains('/', na=False)

goodD = pd.to_datetime(dataF.loc[dataTs, 'ts']) 
badD = dataF.loc[~dataTs, 'ts'] # flag ~ tells just give me the bad ones 

partsTs = badD.str.split(':')
minutesTs = partsTs.str[0].astype(int) # Minutes
secondsTs = partsTs.str[1].astype(float) # Seconds 

transformDates = pd.to_datetime({
    'year': 2026, 
    'month': 2,
    'day': 12,
    'hour': 9,
    'minute': minutesTs,
    'second': secondsTs,
    # 'microsecond': ((secondstr % 1) * 1_000_000).astype(int)
})

dataF["timestamps"] = pd.NaT # Creating a new column 

# Populate the new column with all the formated values
dataF.loc[dataTs, "timestamps"] = goodD
dataF.loc[~dataTs, "timestamps"] = transformDates

# sample it, making sure is correct
sample = dataF[["ticker", "timestamps", "mid"]]
print(sample)

dataF = dataF.sort_values(['ticker', 'timestamps']).reset_index(drop=True)

# Method 1: Count-based (what we just did)
tick_counts = dataF.groupby(['ticker', 'timestamps']).transform('size')
dataF['is_ghost'] = tick_counts > 1

# Method 2: Timestamp-based (second == 0)
dataF['ghost_by_time'] = (
    (dataF['timestamps'].dt.second == 0) & 
    (dataF['timestamps'].dt.microsecond == 0)
)

# Do they match?
both = (dataF['is_ghost'] == dataF['ghost_by_time']).all()
print(f"Both methods agree on every row: {both}")

# If not, show the differences
if not both:
    diff = dataF[dataF['ghost_by_count'] != dataF['ghost_by_time']]
    print(f"Rows where they disagree: {len(diff)}")
    print(diff[['ticker', 'timestamps', 'mid', 'ghost_by_count', 'ghost_by_time']])

# Verify
print(f"Ghost ticks found: {dataF['is_ghost'].sum()}")
print(f"Normal ticks: {(~dataF['is_ghost']).sum()}")

# See the counts distribution
print("\nTicks per timestamp:")
print(tick_counts.value_counts().sort_index())

# --

reduced = dataF.drop_duplicates(subset=['ticker', 'timestamps'], keep='first').copy()
reduced = reduced.sort_values(['ticker', 'timestamps']).reset_index(drop=True)

print(f"Original: {len(dataF)} rows")
print(f"After removing duplicates: {len(reduced)} rows")
print(f"Ghost ticks remaining (1 per cluster): {reduced['is_ghost'].sum()}")

reduced.loc[reduced['is_ghost'], 'mid'] = float('nan')
reduced['mid'] = reduced.groupby('ticker')['mid'].transform(
    lambda x: x.interpolate(method='linear')
)

print(f"After interpolation: {reduced['mid'].isna().sum()} missing values remaining")

for stock in reduced['ticker'].unique():
    stock_data = reduced[reduced['ticker'] == stock]

    plt.figure(figsize=(12, 6))

    normal = stock_data[~stock_data['is_ghost']]
    ghosts = stock_data[stock_data['is_ghost']]

    plt.plot(normal['timestamps'], normal['mid'], color='blue', linewidth=1, label='Normal')
    plt.scatter(ghosts['timestamps'], ghosts['mid'], color='green', s=40, zorder=5, label='Interpolated')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=30))
    plt.xticks(rotation=45)
    plt.title(f'{stock} — Ghost Ticks Replaced by Interpolation')
    plt.xlabel('Time')
    plt.ylabel('Mid Price')
    plt.legend()
    plt.tight_layout()
    plt.show()
