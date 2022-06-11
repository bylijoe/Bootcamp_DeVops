FROM python:3.7-alpine as base

FROM base AS dependencias 

WORKDIR /install

RUN apk add --no-cache gcc musl-dev linux-headers
COPY src/requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


FROM base

COPY --from=dependencias /install  /usr/local

WORKDIR /app
COPY src .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0


EXPOSE 5000

CMD ["flask", "run"]
