# intial stage
FROM python:3.11.0-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    build-essential \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .


RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# Copy app code
COPY . .

# Final stage
FROM python:3.11.0-slim

WORKDIR /app    

# Install only what's needed at runtime
RUN apt-get update && apt-get install -y \
    unixodbc \
    freetds-bin \
    tdsodbc \
    nano \
    net-tools \
    curl \
    telnet \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only the installed Python packages from the builder stage to the final image.
# This avoids reinstalling dependencies, keeps the image smaller, and excludes build tools.
COPY --from=builder /install /usr/local

# Copy the application source code from the builder stage to the final image.
# This ensures the runtime image has the latest app files without rebuilding dependencies.
COPY --from=builder /app /app

# Register the ODBC driver
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

# Expose port and run app
EXPOSE 5000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]