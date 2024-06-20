FROM ubuntu:22.04
RUN apt-get update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN pip install --upgrade pip
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
CMD python3 manage.py runserver 0.0.0.0:8000
