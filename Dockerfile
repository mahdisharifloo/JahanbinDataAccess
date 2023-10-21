# 
# FROM python:slim-buster
# # 
# WORKDIR /code


# RUN apt-get update
# #

# COPY ./requirements.txt /code/requirements.txt

# # 
# RUN pip install  -r /code/requirements.txt




FROM dashboard_api:latest 

WORKDIR /code



COPY ./requirements.txt /code/requirements.txt
RUN pip install  -r /code/requirements.txt



COPY ./ /code/




#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2468"]
CMD ["python","api/main.py"]