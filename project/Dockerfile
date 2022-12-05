# Base Image
FROM python:3.8
# set a key-value label for the Docker image
LABEL maintainer="Thomas Estabrook"
# copy files from the host to the container filesystem. 
# For example, all the files in the current directory
# to the  `/app` directory in the container
COPY techtrends /app
#  defines the working directory within the container
WORKDIR /app
# Expose the application port
EXPOSE 3111
# to install dependencies defined in the requirements.txt file. 
RUN pip install -r requirements.txt
# Initialize the database
RUN python init_db.py
# provide a command to run on container start. 
CMD [ "python", "app.py" ]