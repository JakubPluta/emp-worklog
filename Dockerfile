FROM python:3.12.0-slim-bullseye

ENV PYTHONUNBUFFERED 1
WORKDIR /build

# TODO: poetry instead of pip
# Create venv, add it to path and install requirements
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install uvicorn server
RUN pip install uvicorn[standard]


COPY worklog worklog
COPY migrations migrations
COPY scripts scripts
COPY alembic.ini .
COPY pyproject.toml .


# Create new user to run app process as unprivilaged user
RUN addgroup --gid 1001 --system uvicorn && \
    adduser --gid 1001 --shell /bin/false --disabled-password --uid 1001 uvicorn


RUN chown -R uvicorn:uvicorn /build
CMD bash scripts/init.sh && \
    runuser -u uvicorn -- /venv/bin/uvicorn worklog.main:app --app-dir /build --host 0.0.0.0 --port 8000 --workers 2 --loop uvloop
EXPOSE 8000