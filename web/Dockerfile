# Pulling the base image
FROM python:3.12.3-bullseye

# Create user
RUN groupadd --gid 1000 smartendance && \
useradd --uid 1000 --gid smartendance --shell /bin/bash --create-home smartendance

# Create user directory
RUN mkdir -pm755 /home/smartendance/web

# Setting the working directory
WORKDIR /home/smartendance/web

# Copying all the files to the working directory
COPY . /home/smartendance/web

# Copying .flaskenv file
COPY .flaskenv /home/smartendance/web/

# Installing required dependencies
RUN pip3 install -r requirements.txt --no-cache-dir

# Exposing the port
EXPOSE 5555

# Running the application
CMD ["python3", "wsgi.py"]