FROM python:3.13-slim

WORKDIR /app

RUN pip install livereload

COPY . .

CMD ["livereload", "--port=5500"]
