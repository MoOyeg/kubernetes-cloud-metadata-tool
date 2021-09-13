FROM docker.io/centos@sha256:e4ca2ed0202e76be184e75fb26d14bf974193579039d5573fb2348664deef76e

#ENV Variables
ENV APP_MODULE main:app
ENV APP_CONFIG gunicorn.conf

# Install the required software
RUN yum update -y && yum install git python3 pip3 -y

#Make Application Directory
RUN mkdir /app && cd /app

# Copy Files into containers
COPY ./app /app
COPY ./deploy/gunicorn.conf /app/

#WORKDIR
WORKDIR /app

# Install App Dependecies
RUN pip install -r requirements.txt

#Expose Ports
EXPOSE 8080/tcp

#Change Permissions to allow not root-user work
RUN chmod -R g+rw ./

#Change User
USER 1001

#ENTRY
ENTRYPOINT gunicorn -c $APP_CONFIG $APP_MODULE