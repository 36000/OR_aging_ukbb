FROM rocker/r-ubuntu:20.04

RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.8 python3-pip git
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
RUN update-alternatives --set python /usr/bin/python3.8
RUN pip install pandas numpy tqdm

RUN pip install rpy2
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN apt-get -y install cmake libxml2-dev libssl-dev libnlopt-dev
RUN R -e "install.packages('ez',dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages('mice',dependencies=TRUE, repos='http://cran.rstudio.com/')"
