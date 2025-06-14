# Importing the dataset
import pandas as pd
import numpy as np
df = pd.read_csv('first_25000_rows.csv')
print(df.head())
df.info()

# Create previous state columns
df['prev_bid_px'] = df['bid_px_00'].shift(1)
df['prev_bid_sz'] = df['bid_sz_00'].shift(1)
df['prev_ask_px'] = df['ask_px_00'].shift(1)
df['prev_ask_sz'] = df['ask_sz_00'].shift(1)


# Calculate delta_bid
bid_conditions = [
    df['bid_px_00'] > df['prev_bid_px'],  # Price went up
    df['bid_px_00'] == df['prev_bid_px'], # Price is the same
    df['bid_px_00'] < df['prev_bid_px']   # Price went down
]
bid_outcomes = [
    df['bid_sz_00'],                     # Imbalance is the new size
    df['bid_sz_00'] - df['prev_bid_sz'], # Imbalance is the change in size
    0                                    # Orders were pulled, no contribution to OFI
]
df['delta_bid'] = np.select(bid_conditions, bid_outcomes, default=0)


# Calculate delta_ask using np.select
ask_conditions = [
    df['ask_px_00'] < df['prev_ask_px'],  # Price went down
    df['ask_px_00'] == df['prev_ask_px'], # Price is the same
    df['ask_px_00'] > df['prev_ask_px']   # Price went up
]
ask_outcomes = [
    df['ask_sz_00'],                     # Imbalance is the new size
    df['ask_sz_00'] - df['prev_ask_sz'], # Imbalance is the change in size
    0                                    # Orders were pulled, no contribution to OFI
]
df['delta_ask'] = np.select(ask_conditions, ask_outcomes, default=0)


# Final OFI Calculation
df['best_level_ofi'] = df['delta_bid'] - df['delta_ask']


# Print results
print(df[['ts_recv', 'bid_px_00', 'bid_sz_00', 'ask_px_00', 'ask_sz_00', 'best_level_ofi']].head(10))

import matplotlib.pyplot as plt

# Added a plot so I could visualize it better
data_slice = df.head(30).copy()


data_slice['color'] = 'green'
data_slice.loc[data_slice['best_level_ofi'] < 0, 'color'] = 'red'


plt.figure(figsize=(16, 8))

# Bar chart
plt.bar(data_slice.index, data_slice['best_level_ofi'],
        color=data_slice['color'],
        label='Best-Level OFI')


plt.title('Best-Level Order Flow Imbalance (First 30 Events)', fontsize=16)
plt.xlabel('Event Index (Timestamp)', fontsize=12)
plt.ylabel('OFI Value (Net Shares)', fontsize=12)

# Add a horizontal line at y=0
plt.axhline(0, color='black', linewidth=1)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Show the plot
plt.show()
