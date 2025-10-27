# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Copy requirements file
COPY ./requirements.txt /code/requirements.txt

# Install necessary tools and dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gnupg \
        curl \
        gcc \
        g++ \
        python3-dev \
        # PostgreSQL dependencies
        libpq-dev \
        postgresql-client \
        # MySQL dependencies
        default-libmysqlclient-dev \
        default-mysql-client \
        # ODBC dependencies
        unixodbc \
        unixodbc-dev \
        odbcinst \
        # Networking and debugging tools
        iputils-ping \
        net-tools \
        telnet \
        lsof \
        wget \
        nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository and install ODBC Driver 17 for SQL Server
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    # Optional: install unixODBC development headers
    && apt-get install -y unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify ODBC driver installation
RUN odbcinst -q -d

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY ./app /code/app

# Copy environment file
COPY ./.env /code/.env

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# # Health check to verify the service is running
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]