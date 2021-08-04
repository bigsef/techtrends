from python:2.7

COPY ./techtrends /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN python init_db.py

Expose 3111

CMD ["python", "app.py"]