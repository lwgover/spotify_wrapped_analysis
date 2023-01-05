import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from os.path import join
from glob import glob
import csv
import sys

def clean_up_dataframe(path):
    #initialize dataframe
    df = pd.concat([pd.read_json(f) for f in glob(join(path, "StreamingHistory*.json"))])
    df = df[pd.to_datetime(df["endTime"]).dt.year <= 2022] # en

    #clean up dataframe
    df["date"] = pd.to_datetime(df.endTime).dt.date
    df["minutes_played"] = df.msPlayed / 1000 / 60

    top_artists = df.groupby(["artistName"]).agg({"minutes_played": "sum"}).reset_index().sort_values(
            ["minutes_played"], ascending=[False]) 

    df = df.groupby(["artistName", "date"]).agg({"minutes_played": "sum"}).reset_index().sort_values(
            ["date", "minutes_played"], ascending=[True, False])

    #shrink top_artists to just include top artists
    print(list(top_artists["artistName"])[:5])
    top_artists = top_artists[top_artists['artistName'].isin(list(top_artists["artistName"])[:5])]

    #complete df
    top_artists = top_artists.drop(columns=['minutes_played'])
    df = df[df['artistName'].isin(list(top_artists["artistName"])[:5])]
    df = df.drop(columns=['artistName','minutes_played']).merge(top_artists,how='cross').merge(df,how='left')
    df["minutes_played"] = df.groupby('artistName')['minutes_played'].ffill().fillna(0)
    df = df.drop_duplicates()

    #create cumulative minutes for each date
    df["date_cumulative"] = df.groupby(["date"])["minutes_played"].cumsum()
    df = df.merge(df.groupby(["date"])['minutes_played'].sum(),on=['date'])
    df = df.rename(columns={"minutes_played_y": "date_sum","minutes_played_x": "minutes_played"})

    df['artist_proportion'] = df['date_cumulative'] / df['date_sum'] #normalize minutes
    
    return df, top_artists

def plot_normalized_minutes(df):
    df.sort_values(["artistName", "date"])
    df.index = pd.to_datetime(df["date"], infer_datetime_format=True)
    df = df.drop(columns=["date"])
    fig, ax = plt.subplots(figsize=(15, 7.5))
    for x in df["artistName"].drop_duplicates().to_list():
        ax.plot(df[df["artistName"].isin([x])]["artist_proportion"], label=x)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.set_ylabel('Minutes normalized by top artist minutes')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, fancybox=True, shadow=True, 
              ncol=9, title='Artist')
    #plt.savefig('../output/2022_streaming_artists.png', bbox_inches='tight')
    plt.show()


def create_csv(df:pd.DataFrame,top_artists:pd.DataFrame):
#export data in csv to display in processing
    header = ['date'] + list(top_artists['artistName'])[:5]

    with open('spotify_wrapped.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        counter = 0
        curr = []
        for row in list(zip(list(df['date']),list(df['artist_proportion']))):
            if counter <= 0:
                curr += [str(row[0])]
            curr += [row[1]]
            if counter >= 4:
                writer.writerow(curr)
                print(curr)
                curr = []
                counter = -1
            counter +=1
    

# run main function
if __name__ == "__main__":
    try:
        df,top_artists = clean_up_dataframe(sys.argv[1])
        create_csv(df,top_artists) #create comprehensible file
        plot_normalized_minutes(df) #display
    except:
        print("Please provide correct path for your spotify as a command argument")

