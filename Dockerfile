# Use the official Arch Linux base image
FROM archlinux:latest

# Update the package database and upgrade the system
RUN pacman -Syu --noconfirm

# Install dependencies for building Python
RUN pacman -S --noconfirm \
    base-devel \
    openssl \
    zlib \
    xz \
    sqlite \
    bzip2 \
#    tk \
    gdbm \
    libnsl \
    libffi \
    bluez-libs \
    readline \
    libtirpc \
#    python-psycopg2 \
    openbsd-netcat \
    gdal \
    wget

# Set environment variables for Python installation
ENV PYTHON_VERSION=3.12.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Download and compile Python
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xvf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall

# Set Python 3.12.7 as the default Python version
RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python

# Verify the default Python version
RUN python --version

# Update pip to the latest version
RUN python -m pip install --upgrade pip

# Create a directory for the Django project
RUN mkdir -p /app/dojo

# Set the working directory
WORKDIR /app/dojo

# Copy Django project (assuming you have a local project to copy)
COPY dojo /app/dojo

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Install Django 4.2
RUN pip install -r requirements.txt

# Expose port 8000 for Django development server
EXPOSE 8000

# Default command to run a bash shell
# CMD ["bash"]

ENTRYPOINT ["/entrypoint.sh"]
