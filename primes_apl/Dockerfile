FROM ubuntu:20.04

# FROM alpine:3.14
# RUN apk add dpkg
# RUN wget https://ftp.gnu.org/gnu/apl/apl_1.8-1_amd64.deb
RUN apt-get update \
    && apt install -y libcairo2 libpq5 libgtk-3-0 libglib2.0-0  libtinfo5 libfftw3-double3 libpcre2-32-0 \
    && apt-get install -y curl \
    && /usr/bin/curl https://ftp.gnu.org/gnu/apl/apl_1.8-1_amd64.deb --output apl181.deb \
    && dpkg -i apl181.deb

WORKDIR /app

COPY generate_primes.apl primes_apl.sh ./
RUN chmod a+x ./primes_apl.sh

ENTRYPOINT [ "/app/primes_apl.sh", "-l", "1000000", "-t", "5" ]