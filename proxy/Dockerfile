FROM archlinux:latest

USER root

# Clean up the pacman cache after installing dependencies to make the image smaller.
RUN pacman --refresh --sync --noconfirm mitmproxy \
  && pacman --sync --clean --clean --noconfirm

COPY main.sh /root/main.sh
COPY addons/ /root/addons/

ENTRYPOINT ["/root/main.sh"]
