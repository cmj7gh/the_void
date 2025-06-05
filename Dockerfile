FROM python:3.11-slim

# Install system dependencies for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app 
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
COPY . .
#RUN python manage.py collectstatic --noinput
CMD [ "gunicorn", "-b 0.0.0.0:8000", "the_void.wsgi:application", "--log-level=debug" ]