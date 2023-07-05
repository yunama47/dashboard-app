import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
sns.set(style='dark')

# Helper function 
def kelompokwaktu(hr):
  if hr in [0,1,2,19,20,21,22,23]:
    return "malam"
  if hr in [3,4,5,6,7,8,9]:
    return 'pagi'
  if hr in [10,11,12,13,14]:
    return 'siang'
  if hr in [15,16,17,18]:
    return 'sore'
  
def get_corr(_with):
  corr_index = ["month","holiday","weekday","working day","weather","temperature","feeling temperature","humidity","windspeed",]
  corr = day_df.loc[:,parameters].corrwith(_with)
  corr.index = corr_index
  corr = corr.abs().reset_index().rename({0:'corr'}, axis=1)
  return corr

def corr_barplot(_with, title="all user count"):
  corr = get_corr(_with)
  fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(15, 15))
  
  colors1 = [ "#FDBB44","#FDBB44","#FDAA88", "#FDAA88","#D3D3D3"]
  colors2 = [ "#FB4444","#FB4444","#D3D3D3", "#D3D3D3","#D3D3D3"]

  sns.barplot(x='corr', y='index',data=corr.sort_values(by="corr",ascending=False).head(), palette=colors1, ax=ax[0])
  ax[0].set_ylabel(None)
  ax[0].set_xlabel(None)
  ax[0].set_title("Most Correlation", loc="center", fontsize=15)
  ax[0].tick_params(axis ='y', labelsize=12)

  sns.barplot(x='corr', y='index',data=corr.sort_values(by="corr",ascending=True) .head(), palette=colors2, ax=ax[1])
  ax[1].set_ylabel(None)
  ax[1].set_xlabel(None)
  ax[1].invert_xaxis()
  ax[1].yaxis.set_label_position("right")
  ax[1].yaxis.tick_right()
  ax[1].set_title("Least Correlation", loc="center", fontsize=15)
  ax[1].tick_params(axis='y', labelsize=12)
  
  plt.suptitle(f"Most and Least correlation with {title} ", fontsize=20)
  return plt.gcf()

def plot_per_hours(day):
  one_day = hour_df.loc[hour_df.dteday == day].copy()
  one_day.casual = (one_day.casual - one_day.casual.mean()) / one_day.casual.std()
  one_day.registered = (one_day.registered - one_day.registered.mean()) / one_day.registered.std()

  plt.figure(figsize=(12, 5))

  plt.plot(one_day['hr'], one_day['casual'], color='#66ff66')
  plt.plot(one_day['hr'], one_day['registered'], color='#ff6666')
  plt.title(f'user stats on {day.date()}')
  plt.xticks(one_day['hr'])
  plt.yticks([])
  plt.xlabel('hour',size=15)
  plt.ylabel(None)
  plt.legend(['casual user','registered user'])
  return plt.gcf()

# Load data
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

parameters = ["mnth","holiday","weekday","workingday","weathersit","temp","atemp","hum","windspeed"]
day_df.weekday.mask(day_df.weekday==0,7, inplace=True)# menggubah indeks hari minggu = 7
hour_df['hr_group'] = hour_df.hr.apply(kelompokwaktu) # mengelompokkan waktu
# mengubah dteday menjadi tipe datetime
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
# Menyiapkan berbagai dataframe
by_hr_group =  hour_df.groupby(by='hr_group').agg({
                    'casual':'sum',
                    'registered':'sum',
                }).reset_index()
by_weekday =  day_df.groupby(by='weekday').agg({
                    'casual':'sum',
                    'registered':'sum',
                }).reset_index()


# Filter data
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.header('Bike Sharing Dashboard :sparkles:')
    today = st.date_input(
        label='Pilih hari',min_value=min_date,
        max_value=max_date,
        value=min_date
    )
    today = datetime.datetime(today.year,today.month,today.day)
    corr_with = st.radio(
    label="Which type of user you want to know the correlation with the parameters?",
    options=('All user', 'Casual user', 'Registered user'),
    horizontal=False
)


#plot daily stats
st.header('Bike Sharing Dashboard :sparkles:')
st.subheader(f'Daily Stats')

col1, col2 = st.columns(2)

with col1:
    total_user = hour_df.loc[hour_df.dteday == today].cnt.sum()
    st.metric("Total user", value=total_user)

with col2:
    avg_temp = day_df.loc[day_df.dteday == today].temp * 41
    degree_sign = u"\N{DEGREE SIGN}"
    st.metric("Average Temperature", value=f"{float(avg_temp):.2f}{degree_sign}C")

dailly_stat = plot_per_hours(today)
st.pyplot(dailly_stat)

# plot perbandingan preferensi hari user

X = ['senin','selasa','rabu','kamis','jumat','sabtu','minggu']
X_axis = by_weekday.weekday

# normalisasi
by_weekday.casual = (by_weekday.casual - by_weekday.casual.mean()) / by_weekday.casual.std()
by_weekday.registered = (by_weekday.registered - by_weekday.registered.mean()) / by_weekday.registered.std()

st.subheader("Perbandingan preferensi hari pengguna casual dan registered")
plt.subplots(1,1)
plt.bar(X_axis, by_weekday.casual, 0.04, color='#dadada')
plt.bar(X_axis, by_weekday.registered, 0.04, color='#dadada')

plt.plot(X_axis, by_weekday.casual, label = 'casual', color='#4afa4a')
plt.plot(X_axis, by_weekday.registered, label = 'registered', color='#4a4afa')

plt.xticks(X_axis, X)
plt.yticks([])
plt.xlabel(None)
plt.ylabel("user stats")
plt.legend()
st.pyplot(plt.gcf())

# pie chart, jam-jam user sering bersepeda
st.subheader("Jam saat user paling sering menggunakan sepeda")
plt.subplot()
pie = plt.gcf()
pie.set_size_inches(15,15)
colors = ('#8888ff', '#ddff00', '#fedadf', '#ffaa55')

plt.subplot(1,2,1)
plt.title('Casual users')
plt.pie(
    x=by_hr_group.casual,
    autopct='%1.1f%%',
    colors=colors,
    explode=(0, 0, 0.1, 0)
)

plt.subplot(1,2,2)
plt.title('Registered users')
plt.pie(
    x=by_hr_group.registered,
    autopct='%1.1f%%',
    colors=colors,
    explode=(0, 0, 0, 0.1)
)
plt.legend(by_hr_group.hr_group)
st.pyplot(pie)

# Parameters correlation
st.subheader(f"Most and Least correlation with {corr_with}")
if corr_with == 'All user':
    corrplot = corr_barplot(day_df.cnt,corr_with)
    st.pyplot(corrplot)
if corr_with == 'Casual user':
    corrplot = corr_barplot(day_df.casual,corr_with)
    st.pyplot(corrplot)
if corr_with == 'Registered user':
    corrplot = corr_barplot(day_df.registered,corr_with)
    st.pyplot(corrplot)
