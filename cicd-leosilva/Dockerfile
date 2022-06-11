FROM leosn/base-jenkins-agent 

# install terraform

RUN apt-get update && apt-get install -y gnupg unzip software-properties-common curl 

RUN curl -fsSL https://apt.releases.hashicorp.com/gpg |  apt-key add -

RUN apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"

RUN apt-get update && apt-get install terraform

# install awscliv2

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
unzip -q awscliv2.zip && \
./aws/install

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]