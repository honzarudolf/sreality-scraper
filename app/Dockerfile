FROM python:3.8
RUN pip install --upgrade pip && pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false --local && poetry install --no-dev
COPY . .
CMD ["app/app.py"]