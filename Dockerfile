FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

COPY ./app /app

# # install python modules
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt