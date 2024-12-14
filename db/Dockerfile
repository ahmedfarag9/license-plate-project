# Use the official MySQL image from the Docker Hub
FROM mysql:latest

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=license_plate_db
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=userpassword

# Expose the default MySQL port
EXPOSE 3306

# Copy the initialization script to the Docker container
COPY ./init.sql /docker-entrypoint-initdb.d/

# Run the MySQL server
CMD ["mysqld"]