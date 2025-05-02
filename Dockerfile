FROM pix-id-base:latest

WORKDIR /app
COPY . .

RUN mkdir -p app/static/uploads app/static/detected_faces

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]