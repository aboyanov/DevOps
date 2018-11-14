# Scripts, how-tos and tipc and tricks for AWS

## Authenticate to AWS Docker Registry in order to push image(It will use the aws-cli credentials):
  - docker build -t 103293740570.dkr.ecr.eu-west-1.amazonaws.com/exchange/php:v_0.1 .
  - **$(/usr/local/bin/aws ecr get-login --no-include-email)**
  - docker push 103293740570.dkr.ecr.eu-west-1.amazonaws.com/exchange/php:v_0.1
