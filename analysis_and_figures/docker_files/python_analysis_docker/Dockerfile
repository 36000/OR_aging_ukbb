FROM rocker/r-ubuntu:20.04

RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.8 python3-pip git
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
RUN update-alternatives --set python /usr/bin/python3.8
RUN pip install pandas


COPY ./package.json ./package.json

RUN apt-get -y install curl gnupg graphviz
RUN curl -sL https://deb.nodesource.com/setup_14.x  | bash -
RUN apt-get -y install nodejs
RUN npm install
RUN npm install vega-lite vega-cli canvas

RUN pip install --no-cache-dir git+https://github.com/richford/skmediate.git@enh/precision-estimator
RUN pip install altair altair_transform altair_saver
RUN pip install pygam statsmodels xgboost fracridge
RUN pip install neuropythy configparser
RUN pip install selenium seaborn
RUN pip install git+https://github.com/36000/pymatch.git@ebcb236e206ad30ad4de825d9db32ac776ef396c#egg=pymatch
RUN pip install tensorflow shap==0.40.0 pydot pydotplus
RUN pip install git+https://github.com/richford/AFQ-Insight.git
RUN pip install scipy==1.8.0
RUN pip install scikit-learn==1.0.0 numpy==1.21
