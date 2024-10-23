FROM ubuntu:24.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

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

ARG USER_NAME=vscode
ARG USER_UID=1001
ARG USER_GID=$USER_UID

ENV ENV=dev
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

# disable git ssl verify
RUN git config --global http.sslverify false

WORKDIR /root

# clean
RUN rm -rf /tmp/*

RUN chown -R ${USER_NAME} /root

USER vscode
ENV PATH=$PATH:/home/vscode/.local/bin

CMD /bin/zsh -c "while sleep 1000; do :; done"

# TODO
# error: could not write config file /home/vscode/.gitconfig: Device or resource busy
# agregar postCreatedCommand para instalar dependencias
# agregar descarga de datos
# actualmente no se pueden guardar los archivos modificados (fixear)
# limpiar este archivo
