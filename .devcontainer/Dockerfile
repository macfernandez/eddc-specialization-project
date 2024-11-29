FROM openstax/selenium-chrome

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

ARG USER_NAME
RUN echo ${USER_NAME}

USER root

WORKDIR /root

RUN apt-get update \
    && apt-get install -y sudo \
    && adduser $USER_NAME sudo \
    && echo $USER_NAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \
    && chmod 0440 /etc/sudoers.d/$USER_NAME \
    && usermod -aG sudo $USER_NAME \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/* \
    && rm -rf /var/lib/apt/lists/*

RUN chown -R ${USER_NAME} /root

RUN git config --global http.sslverify false \
    && git config --system core.pager more \
    && git config --global --add safe.directory /workspace \
    && git config --system --add safe.directory /workspace

USER $USER_NAME