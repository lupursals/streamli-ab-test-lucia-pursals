# This is the file I have used to download the dataset

import seaborn as sns
import pandas as pd

# Show available datasets
print(sns.get_dataset_names())

# I have chosen the dimaonds dataset
df = sns.load_dataset("diamonds")  
print(df.head())  

# Save to a CSV file
df.to_csv("diamonds.csv", index=False)

print("Diamonds dataset saved as 'diamonds.csv'")

