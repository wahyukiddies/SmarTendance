# Pulling the base image
FROM python:3.12.3-bullseye

# Create user
RUN groupadd --gid 1000 smartendance && \
useradd --uid 1000 --gid smartendance --shell /bin/bash --create-home smartendance

# Create user directory
RUN mkdir -pm755 /home/smartendance/web

# Setting the working directory
WORKDIR /home/smartendance/web

# Copying all the files to the working directory, including .flaskenv file
COPY . /home/smartendance/web

# Download and set permission for wait-for-it.sh
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /home/smartendance/web/wait-for-it.sh
RUN chmod +x /home/smartendance/web/wait-for-it.sh

# Installing required dependencies
RUN pip3 install -r requirements.txt --no-cache-dir
# Add execute permission to the entrypoint script
RUN chmod +x entrypoint.sh

# Exposing the port
EXPOSE 5000

# Running the application via entrypoint script
CMD [ "./entrypoint.sh" ]