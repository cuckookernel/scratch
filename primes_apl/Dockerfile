FROM gcc:4.9 AS build

# FROM alpine:3.14
# RUN apk add dpkg
# RUN wget https://ftp.gnu.org/gnu/apl/apl_1.8-1_amd64.deb
RUN apt-get update
  #  && apt install -y libcairo2 libpq5 libgtk-3-0 libglib2.0-0 \
  #       libtinfo5 libfftw3-double3 libpcre2-32-0

# RUN apt-get install -y git
    # && apt-get install -y curl

WORKDIR /gnu_apl_repo
RUN git clone https://git.savannah.gnu.org/git/apl.git

WORKDIR /gnu_apl_repo/apl/trunk

RUN echo "pwd: " && pwd
RUN chmod a+x ./configure
RUN make install

# RUN apt-get install make && apt-get install -y  gcc

FROM build

WORKDIR /app

COPY generate_primes.apl primes_apl.sh ./
RUN chmod a+x ./primes_apl.sh

ENTRYPOINT [ "/app/primes_apl.sh", "-l", "1000000", "-t", "5" ]
# ENTRYPOINT [ "apl" ]