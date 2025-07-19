FROM quay.io/centos/centos:stream9
MAINTAINER yogeshvk1209@gmail.com
# Install Python 3.9, pip and sudo
RUN dnf install -y epel-release && \
    dnf install -y python39 python39-pip sudo && \
    dnf clean all
# Add taskUser and provide sudo access
RUN useradd -m taskuser && echo "taskuser:taskuser" | chpasswd && echo 'taskuser ALL=(ALL:ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo
# Install app dependencies
COPY ./src/ /src/
RUN pip3.9 install -r /src/requirements.txt
# Start app source
EXPOSE  8080
USER taskuser
CMD ["python3.9", "/src/pytask.py", "-p 8080"]
