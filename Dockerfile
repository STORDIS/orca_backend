FROM python:3.10
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
CMD python3 manage.py makemigrations log_manager && \
    python3 manage.py migrate && \
    export DJANGO_SUPERUSER_PASSWORD=admin && \
    python manage.py createsuperuser --username=admin --email=admin@example.com --noinput && \
    python3 manage.py runserver 0.0.0.0:8000
