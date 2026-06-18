# Get the meinappnest code
FROM alpine:latest as cloner

ARG CHANNEL
ARG VERSION

RUN apk update && apk upgrade && \
    apk add --no-cache git

RUN git clone https://github.com/Action3062/my-fun-api.git /source

# 
FROM python:3.12

# 
WORKDIR /code

# 
COPY --from=cloner /source/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY --from=cloner /source/app /code/app

# 
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]