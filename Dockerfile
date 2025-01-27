FROM python:3.12
RUN pip install poetry
WORKDIR /orca_backend

COPY ./pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction

COPY . .

## Check if ORCASK app is present, if yes install its dependencies.
RUN test -d ORCASK \
    && cd ORCASK \
    && poetry install --no-interaction \
    || echo "There is no ORCASK app in orca_backend, Skipping installation of dependencies of ORCASK."
RUN rm -rf /root/.cache/pypoetry

EXPOSE 8000
CMD cp -n /usr/local/lib/python3.10/site-packages/orca_nw_lib/orca_nw_lib_logging.yml ./orca_nw_lib_logging.yml && \
    cp -n /usr/local/lib/python3.10/site-packages/orca_nw_lib/orca_nw_lib.yml ./orca_nw_lib.yml && \
    python3 manage.py makemigrations network orca_setup state_manager log_manager fileserver && \
    python3 manage.py migrate && \
    export DJANGO_SUPERUSER_PASSWORD=admin && \
    python manage.py createsuperuser --username=admin --email=admin@example.com --noinput || true && \
    python3 manage.py runserver 0.0.0.0:8000