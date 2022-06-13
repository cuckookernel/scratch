FROM python:3.8.5

RUN pip install --upgrade pip \
    && pip install wheel \
    && pip install pandas \
    && pip install openpyxl \
    && pip install bokeh

WORKDIR /app

COPY  main.py ./nine_box/
COPY  Resultados_de_performance.xlsx .

EXPOSE 5006

# ENV DATABASE_URL postgres://postgres:password@db:5432/ddelivery
ENTRYPOINT ["bokeh", "serve", "--show", "nine_box"]
