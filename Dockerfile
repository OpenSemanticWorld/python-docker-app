#
FROM python:3.9

# 
WORKDIR /app

# 
COPY ./app /app

# 
#RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN find /app -name "requirements.txt" -type f -exec pip install -r '{}' ';'

# 
#CMD ["uvicorn", "app.src:main_app", "--host", "0.0.0.0", "--port", "80"]
#CMD [ "python3", "app/main.py" ]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
