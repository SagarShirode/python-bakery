# Use the official Python image from the Docker Hub
FROM almalinux:8.10

# Install the necessary packages including pkg-config, cairo, gobject-introspection, and other dependencies

RUN yum -y update && \
    yum -y install epel-release && \
    yum -y install \
    gcc \
    make \
    python3-pip \
    python3-devel \
    cairo-devel \
    gobject-introspection-devel \
    mariadb-devel \
    systemd-devel \
    gtk3 \
    python3-gobject \
    glib2-devel \
    libffi-devel


# Set the working directory in the container
WORKDIR /app

RUN pip3 install --upgrade pip
# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install the dependencies 
RUN pip3 install -r requirements.txt
RUN pip3 install dbus-python
# Copy the current directory contents into the container
COPY . .

# Expose the port that Flask will run on
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]

