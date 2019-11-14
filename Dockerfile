FROM python
COPY . /app
WORKDIR /app
RUN pip install --default-timeout=100 -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
