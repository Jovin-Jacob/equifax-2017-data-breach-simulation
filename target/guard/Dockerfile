FROM python:3.12-alpine
WORKDIR /app
COPY guard.py /app/guard.py
RUN chmod 0444 /app/guard.py
USER 65534:65534
EXPOSE 8081
CMD ["python", "-u", "/app/guard.py"]
