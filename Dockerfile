FROM registry.access.redhat.com/ubi8:8.6-943

#ENV Variables
ENV APP_MODULE main:app
ENV APP_CONFIG gunicorn.conf

# Install the required software
RUN yum update -y && yum install -y git python38 python38-pip && \
    yum remove python36

#Make Application Directory
RUN mkdir /app && cd /app

# Copy Files into containers
COPY ./app /app
COPY ./deploy/gunicorn.conf /app/

#WORKDIR
WORKDIR /app

# Install App Dependecies
RUN pip3 install -r requirements.txt

#Expose Ports
EXPOSE 16261/tcp

#Change Permissions to allow not root-user work
RUN chmod -R g+rw ./

#Change User
USER 1001

#ENTRY
ENTRYPOINT gunicorn -c $APP_CONFIG $APP_MODULE