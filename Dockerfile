FROM python:3.14-alpine AS deps

WORKDIR /builder
COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev linux-headers && CFLAGS="-Wno-error=int-conversion" pip install --no-cache-dir -r ./requirements.txt

FROM python:3.14-alpine AS minifier

WORKDIR /src
RUN pip install --no-cache-dir python-minifier
COPY main.py .
COPY functions.py .
RUN pyminify --in-place \
             --remove-literal-statements \
             --rename-globals \
             --preserve-globals conf,esphome_toggle,miot_fan_toggle,wol,hass_toggle,hass_climate_toggle \
             --remove-asserts \
             --remove-debug \
             --prefer-single-line \
             .

FROM python:3.14-alpine

WORKDIR /homeswiftpackets
COPY --from=deps /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=minifier /src/*.py ./
RUN adduser -D homeswiftpackets
USER homeswiftpackets
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python3", "./main.py"]