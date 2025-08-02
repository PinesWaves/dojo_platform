# Usa imagen oficial de Arch Linux
FROM archlinux:latest

# Actualiza sistema e instala dependencias necesarias
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    base-devel openssl zlib xz sqlite bzip2 gdbm libnsl libffi \
    bluez-libs readline libtirpc openbsd-netcat gdal wget \
    nginx git

# Variables de entorno
ENV PYTHON_VERSION=3.12.7 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Descarga y compila Python
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xvf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    ln -sf /usr/local/bin/python3.12 /usr/bin/python

RUN python --version && python -m pip install --upgrade pip

# Crear directorio del proyecto
RUN mkdir -p /app/dojo
WORKDIR /app/dojo

# Copiar archivos
COPY dojo /app/dojo
COPY dojo/entrypoint.sh /entrypoint.sh
COPY dojo/requirements.txt /app/dojo/requirements.txt

RUN chmod +x /entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
