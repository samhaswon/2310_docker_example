# syntax=docker/dockerfile:1

# We are going to use a build stage to build our dependencies to minimize the size of our resulting image
FROM python:3-alpine as build-stage

# Start by making a directory to build wheels in
RUN mkdir /svc
WORKDIR /svc

# Copy the requirements file into this directory from the project repository
COPY requirements.txt /svc

# Install required apk packages
RUN echo "***** Getting required packages *****" && \
    # This container is based on alpine Linux, so we use the `apk` package manager
    apk add --no-cache --update  \
    # gcc, g++, musl-dev, linux-headers, and python3-dev are required to build some of the dependencies of this application
    gcc \
    musl-dev \
    linux-headers \
    python3-dev \
    g++ \
    git && \
    # Upgrade the pip version of the base container to build the dependencies
    pip install --upgrade pip

# Build dependencies into Python wheels, a method of distributing Python packages
RUN echo "***** Building dependencies *****" && \
    pip wheel -r /svc/requirements.txt --wheel-dir=/svc/wheels

# This is our final stage where we will pull everything together
FROM python:3-alpine as application

# This line is required for things like print statements to appear in the container's logs
ENV PYTHONUNBUFFERED=TRUE

# Get build-stage files we built earlier
COPY --from=build-stage /svc /usr/src/app

# Change our working directory to where we placed our wheels
WORKDIR /usr/src/app

# Install the built wheels of our dependencies
RUN echo "***** Installing dependencies *****" && \
    pip install --no-index --find-links=/usr/src/app/wheels -r requirements.txt

# Copy all of our code into the container, making it executable with the `chmod` flag
COPY --chmod=0755 . .

# Expose port 5000 where our app will listen
EXPOSE 5000

# We are using waitress, which catches SIGTERM and SIGINT. Docker eventually sends SIGKILL to the main process (PID 1) which will stop our server but it takes time to do this
STOPSIGNAL SIGKILL

# This is our app's start command. Depending on what your container requires to start, ENTRYPOINT works similarly but does not pass signals
CMD [ "/usr/src/app/start.sh" ]

# Using HEALTHCHECK, we can determine if our application is healthy
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD wget http://localhost:5000/health -q -O - > /dev/null 2>&1