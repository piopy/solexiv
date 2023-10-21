FROM python:3.12.0b1-slim

#  arguments
ARG DEV_MODE

# environment
ENV PYTHONFAULTHANDLER=1 \
	PYTHONUNBUFFERED=1 \
	PYTHONHASHSEED=random \
	PIP_NO_CACHE_DIR=off \
	PIP_DISABLE_PIP_VERSION_CHECK=on \
	PIP_DEFAULT_TIMEOUT=100 \
	POETRY_VERSION=1.1.13 \
	POETRY_VERSION=1.3.1 \
	URLLIB_VERSION=1.26.15 \
	DAGSTER_HOME=/opt/dagster/dagster_home 


# create a directory and make it accessible to the user
RUN mkdir /app

# poetry
RUN pip install "poetry==$POETRY_VERSION" "urllib3==$URLLIB_VERSION"

# copy only requirements to cache them in docker layer
WORKDIR /app
COPY src/pyproject.toml /app/

# project initialization
RUN poetry config virtualenvs.create false \
	&& poetry install $(test "${DEV_MODE}" != prototype && echo "--no-dev") --no-interaction --no-ansi

# USER $USERNAME

COPY src/ /app/src/
COPY data/ /app/data/
COPY creds/creds.sample.json /app/creds/creds.json

ENV PYTHONPATH "${PYTHONPATH}:/app/src"
EXPOSE 8181

# run
WORKDIR /app/src/
CMD ["streamlit", "run", "Homepage.py", "--server.port", "8181", "--server.address", "0.0.0.0" , "--browser.gatherUsageStats", "False"]
