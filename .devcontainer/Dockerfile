FROM ubuntu:24.04

ARG USER_NAME=vscode
ARG USER_UID=1001
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USER_NAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USER_NAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USER_NAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \
    && chmod 0440 /etc/sudoers.d/$USER_NAME

RUN apt-get update && apt-get install -y xz-utils

#ENV SHELL=/usr/bin/zsh
#RUN chsh "$USER_NAME" -s "$SHELL"

#RUN chown -R ${USER_NAME} /root
#USER $USER_NAME

CMD /bin/zsh -c "while sleep 1000; do :; done"
