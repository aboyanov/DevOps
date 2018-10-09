#!/bin/bash

### This file will append the following alliases and functions to your ~/.bashrc ###

echo <<EOT >> ~/.bashrc
function set_dkr(){
  export DOCKER_REGISTRY=$1  
}

function get_pods(){
  kubectl get pods --namespace=$NAMESPACE
}

function get_services(){
  kubectl get service --namespace=$NAMESPACE
}

function get_deployments(){
  kubectl get deployment --namespace=$NAMESPACE
}

function set_namespace(){
  export NAMESPACE=$1
}

function klog(){
  kubectl --namespace=$NAMESPACE log $1
}
EOT
