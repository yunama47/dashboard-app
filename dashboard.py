import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
sns.set(style='dark')

# Load data
day_df = pd.read_csv("new_day.csv")
hour_df = pd.read_csv("new_hour.csv")

# helper function
def plot_per_hours(day, df):
  one_day = df.loc[df.dteday == day].copy()
  # normalisasi
  one_day.casual = (one_day.casual - one_day.casual.mean()) / one_day.casual.std()
  one_day.registered = (one_day.registered - one_day.registered.mean()) / one_day.registered.std()

  plt.figure(figsize=(12, 5))
  plt.plot(one_day['hr'], one_day['casual'], color='#66ff66')
  plt.plot(one_day['hr'], one_day['registered'], color='#ff6666')
  plt.title(f'user stats on {day.date()}')
  plt.xticks(one_day['hr'])
  plt.yticks([])
  plt.xlabel('hour',size=15)
  plt.ylabel("Stats")
  plt.legend(['casual user','registered user'])
  return plt.gcf()

def pie_chart_time():
    by_hr_group =  hour_df.groupby(by='hr_group').agg({
                    'casual':'sum',
                    'registered':'sum',
                }).reset_index()
    fig = plt.gcf()
    fig.set_size_inches(15,15)
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
    return fig

def plot_weekly():
    by_weekday =  day_df.groupby(by='weekday').agg({
                    'casual':'sum',
                    'registered':'sum',
                    'cnt':'sum'
                }).reset_index()
    by_weekday.weekday = ['senin','selasa','rabu','kamis','jumat','sabtu','minggu']
    norm_casual = (by_weekday.casual - by_weekday.casual.mean()) / by_weekday.casual.std()
    norm_registered = (by_weekday.registered - by_weekday.registered.mean()) / by_weekday.registered.std()
    fig, ax = plt.subplots(1,2,figsize=(15,5))
    ax[0].bar(by_weekday.weekday, norm_casual, 0.04, color='#dadada')
    ax[0].bar(by_weekday.weekday, norm_registered, 0.04, color='#dadada')
    ax[0].plot(by_weekday.weekday, norm_casual, label = 'casual user', color='#4afa4a')
    ax[0].plot(by_weekday.weekday, norm_registered, label = 'registered user', color='#4a4afa')
    ax[0].set_yticks([])
    ax[0].set_ylabel("user stats")
    ax[0].set_title("Perbandingan preferensi hari pengguna casual dan registered")
    ax[0].legend()

    colors = ["#A3DBA3","#A3DBA3", "#A3DBA3","#A3DBA3", "#A3DBA3","#A3DBA3", "#006600",]
    ax[1].barh('weekday', 'cnt',data=by_weekday.sort_values(by='cnt') ,color = colors)
    ax[1].set_xlabel("user count")
    ax[1].set_title("Keramaian pengguna berdasarkan hari dalam minggu")
    return fig

def plot_yearly(new_hour_df, year=None):
  if year is not None:
    new_hour_df = new_hour_df[new_hour_df.yr==year].copy()
  by_month = new_hour_df.groupby(by='mnth').agg({
                      'cnt':'sum'
                  }).reset_index()
  by_month.mnth = ['Januari','Februari', 'Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
  by_season = new_hour_df.groupby(by='season').agg({
                      'cnt':'sum'
                  }).reset_index()
  by_season.season = ['spring', 'summer', 'fall', 'winter']
  fig, ax = plt.subplots(1,2,figsize=(15,5))
  ax[0].pie(
      x = by_season.cnt,
      labels = by_season.season,
      autopct='%1.1f%%',
      colors=['#6cf542','#f54e42','#f5a742','#42e9f5'],
      explode=(0, 0, 0.1, 0)
  )
  ax[0].set_title("Jumlah Pengguna Setiap Musim")
  ax[1].bar('mnth', 'cnt',0.5,data=by_month ,color = '#fadada')
  ax[1].plot('mnth', 'cnt',data=by_month ,color = '#fa4a4a')
  ax[1].set_xticks(by_month.mnth, labels=by_month.mnth, rotation=45)
  ax[1].yaxis.tick_right()
  ax[1].yaxis.set_label_position("right")
  ax[1].set_ylabel("user count")
  ax[1].set_title("Jumlah pengguna per bulan")
  plt.suptitle(f"Siklus jumlah pengguna per tahun {2011 if year==0 else 2012 if year==1 else ''}")
  return fig

def get_corr(df, _with):
  parameters = ["mnth","holiday","weekday","workingday","weathersit","temp","atemp","hum","windspeed"]
  corr_index = ["month","holiday","weekday","working day","weather","temperature","feeling temperature","humidity","windspeed",]
  _with = df[_with]
  corr = df.loc[:,parameters].corrwith(_with)
  corr.index = corr_index
  corr = corr.abs().reset_index().rename({0:'corr'}, axis=1)
  return corr

def corr_barplot(df, _with):
  corr = get_corr(df, _with)
  fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

  colors1 = [ "#FDBB44","#FDBB44","#FDAA88", "#FDAA88","#D3D3D3"]
  colors2 = [ "#FB4444","#FB4444","#D3D3D3", "#D3D3D3","#D3D3D3"]

  sns.barplot(x='corr', y='index',data=corr.sort_values(by="corr",ascending=False).head(), palette=colors1, ax=ax[0])
  ax[0].set_ylabel(None)
  ax[0].set_xlabel(None)
  ax[0].set_title("Most Correlation", loc="center", fontsize=15)
  ax[0].tick_params(axis ='y', labelsize=12)

  sns.barplot(x='corr', y='index',data=corr.sort_values(by="corr",ascending=True).head(), palette=colors2, ax=ax[1])
  ax[1].set_ylabel(None)
  ax[1].set_xlabel(None)
  ax[1].invert_xaxis()
  ax[1].yaxis.set_label_position("right")
  ax[1].yaxis.tick_right()
  ax[1].set_title("Least Correlation", loc="center", fontsize=15)
  ax[1].tick_params(axis='y', labelsize=12)

  plt.suptitle(f"Most and Least correlation with '{_with}' column ", fontsize=20)
  return fig

# mengubah dteday menjadi tipe datetime
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

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
    corr_with = st.selectbox(
        label="Korelasikan parameter dengan",
        options=('Semua user', 'Casual user', 'Registered user'),
    )
    year = st.selectbox(
        label="pilih tahun",
        options=(' ', '2011', '2012'),
    )


#plot daily stats
st.header('Bike Sharing Dashboard :sparkles:')
st.subheader(f'Daily Stats')

col1, col2 = st.columns(2)

with col1:
    total_user = day_df.loc[day_df.dteday == today].cnt
    st.metric("Total user", value=total_user)

with col2:
    avg_temp = day_df.loc[day_df.dteday == today].temp * 41
    degree_sign = u"\N{DEGREE SIGN}"
    st.metric("Average Temperature", value=f"{float(avg_temp):.2f}{degree_sign}C")

dailly_stat = plot_per_hours(today, hour_df)
st.pyplot(dailly_stat)

# plot weekly days
st.subheader('Visualisasi jumlah pengguna setiap hari dalam seminggu')
time_pie = pie_chart_time()
st.pyplot(time_pie)
weekly_plot = plot_weekly()
st.pyplot(weekly_plot)

# Plot Parameters correlation
st.subheader(f"Korelasi tertinggi dan terendah terhadap '{corr_with}'")
if corr_with == 'Semua user':
    corrplot = corr_barplot(day_df,'cnt')
    st.pyplot(corrplot)
if corr_with == 'Casual user':
    corrplot = corr_barplot(day_df,'casual')
    st.pyplot(corrplot)
if corr_with == 'Registered user':
    corrplot = corr_barplot(day_df,'registered')
    st.pyplot(corrplot)

# plot data tahunan
st.subheader(f"Keramaian pengguna per tahun {year}")
if year == ' ':
    yearly_plot = plot_yearly(day_df)
    st.pyplot(yearly_plot)
elif year == '2011':
    yearly_plot = plot_yearly(day_df,0)
    st.pyplot(yearly_plot)
elif year == '2012':
    yearly_plot = plot_yearly(day_df,1)
    st.pyplot(yearly_plot)
