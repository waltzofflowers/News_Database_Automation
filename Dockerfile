# Use the official Apache Airflow image with Python 3.9
FROM apache/airflow:2.10.4-python3.9

# Copy the requirements.txt file to the container
COPY requirements.txt /opt/airflow/

# Switch to root to install system dependencies
USER root

# Install dependencies: build tools, ODBC Driver 17 for SQL Server, and required libraries
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    gcc \
    python3-dev \
    libsasl2-dev \
    libssl-dev \
    && apt-get clean

# Set environment variable for ODBCINI file location
ENV ODBCINI=/etc/odbc.ini

# Switch back to the airflow user (best practice)
USER airflow

# Install the Python dependencies listed in the requirements.txt file
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt
