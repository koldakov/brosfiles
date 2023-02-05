FROM python:3.9.10-slim-buster

# Environ
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Arguments
ARG APP_USER=brosfiles
ARG WORK_DIR=/app
ARG VENDOR_STATIC_DIR=${WORK_DIR}/static/vendor
ARG BOOTSTRAP_STATIC_DIR=${VENDOR_STATIC_DIR}/bootstrap
ARG POPPER_STATIC_DIR=${VENDOR_STATIC_DIR}/popper

# Install OS dependencies
COPY install-dependencies.sh /tmp
RUN . /tmp/install-dependencies.sh

# Install python environ
RUN python3 -m venv $VIRTUAL_ENV
COPY requirements.txt /tmp
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Add user
RUN groupadd \
    --system ${APP_USER} \
    && useradd --no-log-init --system --gid ${APP_USER} ${APP_USER}

# Copy project files to the work dir
COPY ./ ${WORK_DIR}

# Download static files
RUN mkdir -p ${BOOTSTRAP_STATIC_DIR}/js
RUN mkdir -p ${POPPER_STATIC_DIR}/js
RUN mkdir -p ${BOOTSTRAP_STATIC_DIR}/css
RUN wget https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.min.js -P ${BOOTSTRAP_STATIC_DIR}/js
RUN wget https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js -P ${POPPER_STATIC_DIR}/js
RUN wget https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css.map -P ${BOOTSTRAP_STATIC_DIR}/css
RUN wget https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css -P ${BOOTSTRAP_STATIC_DIR}/css

# Set owner to the project
RUN chown -R ${APP_USER}:${APP_USER} ${WORK_DIR}

# Set work dir
WORKDIR ${WORK_DIR}

# Open ports
EXPOSE 8080

# Set project user
USER ${APP_USER}:${APP_USER}

# Main launch command
CMD ["./entrypoint.sh"]
