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
# View 1 - New York Death from 2019
data[(data.index > '2019-01-01') & ((data["location"] == "New York") | (data["location"] == "New York City"))].plot(figsize=(16,6), title="New York State Death Data 2019-2020")

# View 2 - California Death from 2019
data[(data.index > '2019-01-01') & ((data["location"] == "California"))].plot(figsize=(16,6), title="California State Death Data 2019-2020")

# View 3 - COVID Death Distribution
death_sum = data.loc[data["location"] != "United States", ["location", "death_covid"]].groupby("location").sum().sort_values("death_covid", ascending=False)
death_sum_ny = death_sum[(death_sum.index == "New York City") | (death_sum.index == "New York")].sum()
death_sum.at["New York", "death_covid"] = death_sum_ny
death_sum = death_sum.drop(["New York City"])
death_sum_top = death_sum.iloc[0:5]
death_sum_other = death_sum.iloc[6:].sum()
death_sum_other = death_sum_other.rename("Others")
death_sum_top = death_sum_top.append(death_sum_other)
total = death_sum_top.sum()[0]
fig, axs = plt.subplots(figsize=(16, 6))
death_sum_top.plot.barh(ax=axs, title="COVID Death Distribution")
axs.set_ylabel("Locations")
axs.set_xlabel("Death Number")
for index, value in enumerate(death_sum_top["death_covid"]):
    plt.text(value, index,  s=f"{value}", color="black", fontname='Comic Sans MS', fontsize=12)
    plt.text(value * 0.4, index, s="{0:.2f}%".format(value / total * 100), color="white", fontname='Comic Sans MS', fontsize=12)

# View 4 - Covid Death Rate
population = pd.read_csv("population.csv", index_col="State")
population = population[["Pop"]]
death_sum["population"] = population
death_sum["death_rate_pct"] = death_sum["death_covid"] / death_sum["population"] * 100
death_rate = death_sum.sort_values("death_rate_pct", ascending=False)

death_rate_top = death_rate.iloc[0:5]
fig, axs = plt.subplots(figsize=(16, 6))
death_rate_top["death_rate_pct"].plot.barh(ax=axs, title="COVID Death Rate")
axs.set_ylabel("Locations")
axs.set_xlabel("Death Rate")
for index, value in enumerate(death_rate_top["death_rate_pct"]):
    plt.text(value, index,  s="{0:.4f}%".format(value), color="black", fontname='Comic Sans MS', fontsize=12)

# View 5 - Weekly Average Death Increase in 2020
death_2014_2019 = data[(data.index > "2014-01-01") & (data.index < "2019-12-31")].groupby("location").mean()
death_2020 = data[data.index > "2020-01-01"].groupby("location").mean()
data_avg_death = pd.DataFrame({"average_weekly_death_2014_2019" : death_2014_2019["death_total"], "average_weekly_death_2020" : death_2020["death_total"]}).astype('int64')
data_avg_death["increase"] = data_avg_death["average_weekly_death_2020"] / data_avg_death["average_weekly_death_2014_2019"]
data_avg_top5 = data_avg_death[data_avg_death.index != "United States"].sort_values("increase", ascending=False).head(5)
data_avg_national = data_avg_death[data_avg_death.index == "United States"]
data_avg = pd.concat([data_avg_top5, data_avg_national], axis=0)
fig, axs = plt.subplots(figsize=(12, 6))
data_avg_top5[["average_weekly_death_2014_2019", "average_weekly_death_2020"]].plot.barh(ax=axs, title="Weekly Average Death Increase in 2020")
axs.set_ylabel("Locations")
axs.set_xlabel("Death Number")
for index, value in enumerate(data_avg_top5["average_weekly_death_2014_2019"]):
    plt.text(value + 10, index - .2,  s=f"{value}")
for index, value in enumerate(data_avg_top5["average_weekly_death_2020"]):
    plt.text(value + 10, index + .1,  s=f"{value}")
    
# See results
plt.show()

# --------------------- Data Persistence ---------------------
import h5py
file = h5py.File('result.h5','w')
g1 = file.create_group("death_data")
g2 = file.create_group("weekly_average_death")
g3 = file.create_group("covid_death_summary")
file.close()

# Save death data 2014-2020
data.to_hdf('result.h5', key='death_data', mode='a')

# Save weekly average death data
data_avg_top5.to_hdf('result.h5', key='weekly_average_death', mode='a')

# Save covid death summary data
death_sum_top.to_hdf('result.h5', key='covid_death_summary', mode='a')

# Save covid death rate data
death_rate_top.to_hdf('result.h5', key='covid_death_rate', mode='a')