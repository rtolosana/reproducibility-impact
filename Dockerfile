# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    pandas \
    scipy \
    matplotlib \
    seaborn \
    requests \
    pyalex

# Set the default command to run the python script manually
CMD ["/bin/bash"]

