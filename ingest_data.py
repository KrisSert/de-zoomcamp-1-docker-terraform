from time import time
import os

import pandas as pd
from sqlalchemy import create_engine


def insert_data_in_chunks(filename):
    target_table_name = filename.split('.', 1)[0]

    # create iterable, for inserting data in chunks:
    df_iter = pd.read_csv(filename, iterator=True, chunksize=100000)

    df = next(df_iter)

    if 'tripdata' in filename:
        # convert 2 cols to timestamp
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    # create empty table with same structure as df.
    df.head(n=0).to_sql(name=target_table_name, con=engine, if_exists='replace')

    # insert the first chunk of data
    df.to_sql(name=target_table_name, con=engine, if_exists='append')

    while True:
        try:
            t_start = time()

            df = next(df_iter)
            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
            df.to_sql(name=target_table_name, con=engine, if_exists='append')

            t_end = time()
            print(f'inserted another chunk, took {t_end - t_start} seconds')

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break


# download homework files:
#os.system("wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz -O yellow_tripdata_2021-01.csv.gz")
os.system("wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz -O green_tripdata_2019-09.csv.gz")
os.system("wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv -O zones.csv")

# create postgres connection:
engine = create_engine('postgresql://root:root@pgdatabase:5432/ny_taxi')

insert_data_in_chunks("green_tripdata_2019-09.csv.gz")
insert_data_in_chunks("zones.csv")
