FROM python:3.14-alpine AS deps

WORKDIR /builder
COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev linux-headers
RUN CFLAGS="-Wno-error=int-conversion" pip install --no-cache-dir -r ./requirements.txt

FROM python:3.14-alpine AS minifier

WORKDIR /src
RUN pip install --no-cache-dir python-minifier
COPY *.py ./
RUN for file in *.py; do \
        pyminify "$file" > "$file.tmp" && mv "$file.tmp" "$file"; \
    done

FROM python:3.14-alpine

WORKDIR /homeswiftpackets
COPY --from=deps /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=minifier /src/*.py ./
RUN adduser -D homeswiftpackets
USER homeswiftpackets
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python3", "./main.py"]