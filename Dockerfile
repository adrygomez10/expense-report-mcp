FROM python:3.15.2-slim
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN pip install --no-cache-dir uv==0.13.6 \
    && uv sync --frozen --no-dev
COPY fixtures ./fixtures
RUN useradd --create-home expense \
    && mkdir /data && chown expense:expense /data
USER expense
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/app/.venv/bin/python", "-m", "expense_report.bootstrap"]
CMD ["--fixtures", "/app/fixtures/travel.json", "--database", "/data/expenses.db"]
