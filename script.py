import pandas as pd

# Read the CSV
df = pd.read_csv('./merged.csv')

# Drop duplicates based on weburl only
df = df.drop_duplicates(subset=['weburl'], keep='first')

# Save the cleaned file
df.to_csv('./merged_cleaned.csv', index=False)

print(f"✅ Removed duplicates based on 'weburl'. Final row count: {len(df)}")