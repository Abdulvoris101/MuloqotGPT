FROM python:3.10

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8005

ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
COPY run.sh /app/

CMD ["bash", "/app/run.sh"]
