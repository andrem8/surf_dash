# Surfline Dashboard

## **Architecture**


<img width="4896" alt="Surfline App Architecture" src="https://user-images.githubusercontent.com/5299312/169568492-4ada773b-a77b-485e-9c2e-b4538017ef59.png">


## **Overview**

The pipeline collects data from the surfline API and exports a csv file to S3. Then the most recent file in S3 is downloaded to be ingested into the Postgres datawarehouse. A temp table is created and then the unique rows are inserted into the data tables. Airflow is used for orchestration and hosted locally with docker-compose and mysql. Postgres is also running locally in a docker container. The data dashboard is run locally with ploty.

## **ETL** 

![image](https://user-images.githubusercontent.com/5299312/169564659-76d6cde9-fc59-4d18-9fc4-d8d6f8fa1c0b.png)

## **Data Warehouse - Postgres**

![image](https://user-images.githubusercontent.com/5299312/169566679-3d46d244-b139-4414-a406-c5c18d981ac3.png)

## **Data Dashboard**

![image](https://user-images.githubusercontent.com/5299312/169568656-e6a77014-4bd2-4d21-9236-f24d6f1061b7.png)

## **Learning Resources**

Airflow Basics:

[Airflow DAG: Coding your first DAG for Beginners](https://www.youtube.com/watch?v=IH1-0hwFZRQ)

[Running Airflow 2.0 with Docker in 5 mins](https://www.youtube.com/watch?v=aTaytcxy2Ck)

S3 Basics:

[Setting Up Airflow Tasks To Connect Postgres And S3](https://www.youtube.com/watch?v=30VDVVSNLcc)

[How to Upload files to AWS S3 using Python and Boto3](https://www.youtube.com/watch?v=G68oSgFotZA)

[Download files from S3](https://www.stackvidhya.com/download-files-from-s3-using-boto3/)

Docker Basics:

[Docker Tutorial for Beginners](https://www.youtube.com/watch?v=3c-iBn73dDE)

[Docker and PostgreSQL](https://www.youtube.com/watch?v=aHbE3pTyG-Q)

[Build your first pipeline DAG | Apache airflow for beginners](https://www.youtube.com/watch?v=28UI_Usxbqo)

[Run Airflow 2.0 via Docker | Minimal Setup | Apache airflow for beginners](https://www.youtube.com/watch?v=TkvX1L__g3s&t=389s)

[Docker Network Bridge](https://docs.docker.com/network/bridge/)

[Docker Curriculum](https://docker-curriculum.com/)

[Docker Compose - Airflow](https://medium.com/@rajat.mca.du.2015/airflow-and-mysql-with-docker-containers-80ed9c2bd340)

Plotly:

[Introduction to Plotly](https://www.youtube.com/watch?v=hSPmj7mK6ng)
