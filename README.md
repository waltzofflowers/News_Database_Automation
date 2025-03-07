# News Data Pipeline Project

## Overview
This project automates the collection, transformation, and storage of news data from the past 30 days using the NewsAPI, with daily updates to keep the dataset current. The workflow is powered by Apache Airflow and utilizes a combination of technologies including MSSQL, PostgreSQL, Redis, and Celery, all running on Docker.

## Table of Contents
- [Features](#features)
- [Components](#components)
  - [1. Data Retrieval and Transformation](#1-data-retrieval-and-transformation)
  - [2. Workflow Automation](#2-workflow-automation)
  - [3. Encryption](#3-encryption)
  - [4. Executing SQL](#4-executing-sql)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **Data Source**: NewsAPI for retrieving news data from the past 30 days.
- **Data Storage**: MSSQL for storing the transformed data.
- **Automation**: Apache Airflow orchestrates the workflow, running a scheduler, webserver, and Celery workers to manage tasks.
- **Daily Updates**: After initial data load, the pipeline updates daily to fetch and store only new data.

## Components
### 1. Data Retrieval and Transformation
- **trying.py**: Script that fetches news data for the past 30 days and inserts it into MSSQL.

### 2. Workflow Automation
- **Apache Airflow**: Manages the workflow with the following components:
  - **PostgreSQL**: Backend database for Airflow metadata.
  - **Redis**: Broker for Celery.
  - **Webserver**: User interface for monitoring and managing workflows.
  - **Scheduler**: Triggers tasks according to defined schedules.
  - **Celery Worker**: Executes the tasks.
  - **Docker**: Containerizes the entire setup for easy deployment and management.
- **DAGs Folder**:
  - **trying-dag.py**: Airflow DAG that handles daily data insertion into MSSQL.

### 3. Encryption
- **fernet-finder.ipynb**: Jupyter notebook for generating Fernet keys for encryption during data transmission.
  - Users need to execute this notebook to generate their own Fernet key and paste it into the `airflow.env` file.

### 4. Executing SQL
- **executing.sql**: SQL script that removes overlapping data and inserts only distinct entries into the final table.
  ```sql
  SELECT DISTINCT * INTO News_Final
  FROM News;
  ```

## Usage
- Access the Airflow webserver at `http://localhost:8080` to manage and monitor workflows.
- The pipeline will automatically update the data daily by fetching new articles and inserting them into MSSQL.

## Contributing
Feel free to open issues or submit pull requests. Your contributions are welcome!

## Contact
For any questions or support, please contact cihat.burak.uluturk@gmail.com .
