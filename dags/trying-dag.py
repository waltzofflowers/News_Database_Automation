from airflow import DAG
from airflow.operators.python import PythonOperator
from newsapi import NewsApiClient
import pandas as pd
from datetime import datetime, timedelta
#import pyodbc
from sqlalchemy import create_engine

## CONNECTION ESTABLISHMENT

server = 'server'
database = 'database'
username = 'username'
password = 'password'
driver = 'driver'
port = your_port

def extract(**kwargs):
    # DATABASE CONNECTION
    # conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    # conn = pyodbc.connect(conn_str)

    # API Key
    newsapi = NewsApiClient(api_key='your_api_key')

    # Calculate the date range for the previous day
    today = datetime.today().date()
    previous_day = today - timedelta(days=1)

    # Format the previous day for use in the NewsAPI query
    from_date = previous_day.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    # Get the sources
    sources = newsapi.get_sources()
    df_sources = pd.DataFrame(sources['sources'])

    # Query categories
    q_list = ['economy', 'business', 'money', 'tech', 'science']
    dataframes = {}
    listt = []

    # Loop through categories to fetch articles from the previous day
    for category in q_list:
        all_articles_from_sources = newsapi.get_everything(
            q=category,
            sources='bbc-news,bloomberg,the-verge,abc-news,google-news,business-insider,cnn,the-wall-street-journal,the-washington-times',
            language='en',
            from_param=from_date,  # Only fetch articles from the previous day
            to=to_date,  # Only fetch articles from the previous day
            sort_by='relevancy'
        )

        articles = all_articles_from_sources['articles']
        dataframes[category] = pd.DataFrame(articles)
        listt.append(dataframes[category])

    # Combine all dataframes
    df_total = pd.concat(listt, axis=0)

    kwargs['ti'].xcom_push(key='df_total', value=df_total)

    # Close the connection
    # conn.close()

def transform(**kwargs):
    df_total = kwargs['ti'].xcom_pull(key='df_total', task_ids='extract')

    interests = ['Russia', 'Ukraine', 'Chinese', 'America', 'Erdogan', 'Erdoğan', 'Turkey', 'inflation', 'economy', 'NASA', 'Syria', 'Donald Trump', 'AWS', 'Google']
    df_total['interest'] = df_total['description'].apply(lambda x: next((i for i in interests if i in x), 'Null'))
    df_total['source_name'] = [i.get('name') if isinstance(i, dict) else None for i in df_total['source']]

    df_total['source'] = df_total['source'].astype(str)
    not_null = df_total[df_total['interest'] != 'Null']

    kwargs['ti'].xcom_push(key='df_total', value=df_total)

def load(**kwargs):
    df_total = kwargs['ti'].xcom_pull(key='df_total', task_ids='transform')

    conn_str = f'mssql+pyodbc://{username}:{password}@{server}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
    engine = create_engine(conn_str)


    ## IF YOU WANNA CREATE A NEW DATABASE THAT NOT EXIST

    # newdatabase = 'News_Database'

    # select_query = f"CREATE DATABASE IF NOT EXISTS {newdatabase}"

    # with engine.connect() as connection:
    # result = connection.execute(select_query)


    ## IF YOU WANNA EXECUTE QUERIES WITHIN IT DO IT HERE

    # select_query = "SELECT COUNT(*) FROM News"

    # with engine.connect() as connection:
    #     result = connection.execute(select_query)
    #     df = pd.DataFrame(result.fetchall(), columns=result.keys())

    # print(df.head(5))

    print(pd.io.sql.get_schema(df_total, name="News", con=engine))

    df_total.to_sql(name='News', con=engine, if_exists='append')


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 3,  # Number of retries
    'retry_delay': timedelta(minutes=5),  # Retry delay
    'email_on_failure': False,  # Disable email on failure for simplicity
}

# Correct way to assign start_date as a datetime object
start_date = datetime.now()  # This will include the time and tzinfo (naive datetime by default)

dag = DAG(
    dag_id='trying_dag',
    default_args=default_args,
    start_date=start_date,  # Directly passing a datetime object (with time)
    schedule_interval='@daily',  # This will run the DAG daily
    tags=['test']
)

# Python operator for extraction task
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag
)

extract_task >> transform_task >> load_task
