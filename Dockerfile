FROM python:3.8

EXPOSE 8080
WORKDIR /app

COPY . ./

#copy context.txt 
COPY context.txt /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]