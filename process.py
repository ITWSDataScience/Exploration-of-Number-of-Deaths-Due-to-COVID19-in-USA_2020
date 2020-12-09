import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# --------------------- Data Precess ---------------------
# Reading death data 2014-2018
data_14_18 = pd.read_csv("Weekly_Counts_of_Deaths_by_State_and_Select_Causes__2014-2018.csv", 
                    index_col="Week Ending Date",
                    parse_dates=True)
data_14_18 = data_14_18[["Jurisdiction of Occurrence", "All  Cause"]]
data_14_18 = data_14_18.rename(columns={
    "Jurisdiction of Occurrence" : "location",
    "All  Cause" : "death_total"
})
data_14_18 = data_14_18.rename_axis("date")

# Reading death data 2019-2020
data_19_20 = pd.read_csv("Weekly_Counts_of_Deaths_by_State_and_Select_Causes__2019-2020.csv", 
                    index_col="Week Ending Date", 
                    parse_dates=True)
data_19_20 = data_19_20[["Jurisdiction of Occurrence", "All Cause", "COVID-19 (U071, Multiple Cause of Death)"]]
data_19_20 = data_19_20.rename(columns={
    "Jurisdiction of Occurrence" : "location",
    "All Cause" : "death_total",
    "COVID-19 (U071, Multiple Cause of Death)" : "death_covid"
})
data_19_20 = data_19_20.rename_axis("date")

# Integrate two datasets
data = pd.concat([data_14_18, data_19_20], axis=0)
values = {"death_total" : 0, "death_covid" : 0}
data = data.fillna(value=values)
data["death_non_covid"] = data["death_total"] - data["death_covid"]
data = data.astype({"death_total":"int32", "death_covid":"int32", "death_non_covid":"int32"})
data_covid = pd.pivot_table(data,index="date", columns="location", values="death_covid", fill_value=0).astype(int)
data_total = pd.pivot_table(data,index="date", columns="location", values="death_total", fill_value=0).astype(int)
data_non_covid = pd.pivot_table(data,index="date", columns="location", values="death_non_covid", fill_value=0).astype(int)

# Try print $data $data_covid $data_total $data_non_covid to see its structure.
# print(data)
# print(data_covid)
# print(data_non_covid)
# print(data_total)

# --------------------- Data Visualization ---------------------
# View 1 - Nationwide death in 2020 (COVID vs non-COVID)
data[(data.index > '2020-01-01') & (data["location"] == "United States")].plot.scatter(x="death_covid", y="death_non_covid", alpha=0.5, title="Nationwide Death in 2020")

# View 2 - New York Death from 2019
data[(data.index > '2019-01-01') & ((data["location"] == "New York") | (data["location"] == "New York City"))].plot(figsize=(16,6), title="New York State Death Data 2019-2020")

# View 3 - California Death from 2019
data[(data.index > '2019-01-01') & ((data["location"] == "California"))].plot(figsize=(16,6), title="California State Death Data 2019-2020")

# View 4 - COVID Death Distribution
def my_format(x):
    return '{:.4f}%\n({:.0f})'.format(x, total*x/100)

death_sum = data.loc[data["location"] != "United States", ["location", "death_covid"]].groupby("location").sum().sort_values("death_covid", ascending=False)
death_sum_top = death_sum.iloc[0:5]
death_sum_other = death_sum.iloc[6:].sum()
death_sum_other = death_sum_other.rename("Others")
death_sum_top = death_sum_top.append(death_sum_other)
total = death_sum_top.sum()[0]
my_colors = ['lightblue','lightsteelblue','orange','lightcoral','cornsilk','whitesmoke']
death_sum_top.plot.pie(y="death_covid", figsize=(12,12), title="COVID Death Distribution", autopct=my_format, colors=my_colors)

# See results
plt.show()