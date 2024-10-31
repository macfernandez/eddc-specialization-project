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
