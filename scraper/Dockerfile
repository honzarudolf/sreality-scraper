FROM python:3.8
RUN pip install --upgrade pip && pip install poetry
WORKDIR /scraper
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false --local && poetry install --no-dev
RUN playwright install chromium
RUN playwright install-deps
COPY . .
CMD ["scrapy", "crawl", "sreality_spider"]