FROM ubuntu:24.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

ARG USER_NAME
ARG USER_UID
ARG USER_GID

RUN sed -i 's/# deb-src/deb-src/' /etc/apt/sources.list \
    && apt-get update --fix-missing; exit 0

RUN apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        git-core \
        htop \
        parallel \
        unzip \
        vim \
        wget \
        zsh \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/tmp/* /var/lib/apt/lists/*

RUN apt update && apt install -y \
    apt-transport-https \
    ca-certificates \
    gnupg \
    kmod \
    lsb-release \
    make \
    rsync \
    ssh \
    sudo \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

RUN groupadd --gid $USER_GID $USER_NAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USER_NAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \
    && chmod 0440 /etc/sudoers.d/$USER_NAME \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* \
    && rm -rf /var/lib/apt/lists/*

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

ENV SHELL=/usr/bin/zsh
RUN chsh $USER_NAME -s $SHELL

WORKDIR /root

# clean
RUN rm -rf /tmp/*

RUN chown -R ${USER_NAME} /root

USER $USER_NAME
ENV PATH=$PATH:/home/${USER_NAME}/.local/bin

RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
ENV PATH=$PATH:/home/${USER_NAME}/.local/bin
