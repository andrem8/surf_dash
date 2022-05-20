# We'll start by importing the DAG object
from datetime import timedelta

from airflow import DAG
# We need to import the operators used in our tasks
from airflow.operators.python_operator import PythonOperator
# We then import the days_ago function
from airflow.utils.dates import days_ago

import pandas as pd
import psycopg2
import os
from pysurfline import SurfReport
import boto3
from datetime import date


# get dag directory path
dag_path = os.getcwd()


def download_data():
    params = {
    "spotId": "5842041f4e65fad6a77087f9",
    "days": 1,
    "intervalHours": 1,}

    today = date.today()
    surfdate = today.strftime("%m-%d-%y")

    report = SurfReport(params)
    print(report.api_log)
    
    surf_report = report.df.drop(columns=['utcOffset','swells'])
    surf_report.to_csv(dag_path+'/raw_data/'+ surfdate +'-surf-report.csv',header=False)


def load_s3_data():
    today = date.today()
    surfdate = today.strftime("%m-%d-%y")
    session = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="",)
    s3 = session.resource('s3')
    
    s3.meta.client.upload_file(dag_path+'/raw_data/'+ surfdate +'-surf-report.csv','wavestorm',surfdate +'-surf-report.csv')
    

def download_s3_data():

    s3 = boto3.client('s3',aws_access_key_id="",
    aws_secret_access_key="")

    get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))

    objs = s3.list_objects_v2(Bucket='wavestorm')['Contents']
    last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified)][-1]

    session = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="",)
    s3 = session.resource('s3')
    

    s3.Bucket('wavestorm').download_file(last_added,dag_path+'/processed_data/'+last_added)
    

def load_data():
    #establishing the connection
    conn = psycopg2.connect(
    database="storm", user='postgres', password='wavestorm', host='172.17.0.1', port= '5432'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Executing an MYSQL function using the execute() method
    cursor.execute("select version()")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    print("Connection established to: ",data)

    s3 = boto3.client('s3',aws_access_key_id="",
    aws_secret_access_key="")

    get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))

    objs = s3.list_objects_v2(Bucket='wavestorm')['Contents']
    last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified)][-1]

    command = (
        """

        CREATE TEMPORARY TABLE IF NOT EXISTS staging_surf_report (
            timestamp TIMESTAMP PRIMARY KEY,
            surf_min INTEGER,
            surf_max INTEGER,
            surf_optimalScore INTEGER,
            surf_plus BOOL,
            surf_humanRelation VARCHAR(255),
            surf_raw_min NUMERIC,
            surf_raw_max NUMERIC,
            speed NUMERIC,
            direction NUMERIC,
            directionType VARCHAR(255),
            gust NUMERIC,
            optimalScore INTEGER,
            temperature NUMERIC,
            condition VARCHAR(255)
        );
        """)


    print(command)
    cursor.execute(command)
    conn.commit()


    print(last_added)
    f = open(dag_path+'/processed_data/'+last_added, 'r')
    print(f)
    try:
        cursor.copy_from(f, 'staging_surf_report', sep=",")
        print("Data inserted using copy_from_datafile() successfully....")
    except (Exception, psycopg2.DatabaseError) as err:
        #os.remove(dag_path+'/processed_data/'+last_added)
            # pass exception to function
        print(psycopg2.DatabaseError)
        print(Exception)
        show_psycopg2_exception(err)
        cursor.close()
    conn.commit()


    command = ("""

        INSERT INTO surf_report
      (timestamp, surf_min,surf_max,surf_optimalScore,surf_plus,surf_humanRelation,surf_raw_min,surf_raw_max,speed,direction,directionType,gust,optimalScore,temperature,condition)
        SELECT *
    FROM staging_surf_report
        WHERE NOT EXISTS(SELECT timestamp
                    FROM surf_report 
                   WHERE staging_surf_report.timestamp = surf_report.timestamp);""")


    cursor.execute(command)
    conn.commit()
    conn.close()

# initializing the default arguments that we'll pass to our DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(5)
}

ingestion_dag = DAG(
    'surf_dag',
    default_args=default_args,
    description='Aggregates booking records for data analysis',
    schedule_interval=timedelta(days=1),
    catchup=False
)

task_1 = PythonOperator(
    task_id='download_data',
    python_callable=download_data,
    dag=ingestion_dag,
)

task_2 = PythonOperator(
    task_id='load_s3_data',
    python_callable=load_s3_data,
    dag=ingestion_dag,
)

task_3 = PythonOperator(
    task_id='download_s3_data',
    python_callable=download_s3_data,
    dag=ingestion_dag,
)


task_4 = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=ingestion_dag,
)

#task_3
task_1 >> task_2 >> task_3 >> task_4