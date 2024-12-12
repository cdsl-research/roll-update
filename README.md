# Rolling Update 

In general, this repository includes the contents of the files i used to perform a rolling update on the Wordpress application.

### Contents
- YAML Files
- Python Files
  -rolling update from 6.2.1 version to 6.3.1 version
  -rolling update from 6.1.1 version to 6.3.1 version

### How To Use
first of all, inside a VM with k3s, copy and paste the three YAML files inside a directory
the contents of the directiory should be as the following;
- kustomization.yaml
- mysql-deployment.yaml
- wordpress-deployment.yaml

after saving the three files, use the command below to apply the files 
```
kubectl apply -f wordpress-deployment.yaml -n roll
```
this command deploys the pods in a namespace called "roll"
if you wish to deploy the pods in the default namespace, remove "-n roll" from the command, this will also apply to the commands included in the future.

after deploying the pods, you can check the status of the pods with the following command;
```
kubectl get pod -n roll
```
the expected outcome should be like this
```
NAME                               READY   STATUS    RESTARTS      AGE
wordpress-c8d76b68-64kpf           1/1     Running   1 (10m ago)   12m
wordpress-c8d76b68-n98sc           1/1     Running   0             12m
wordpress-c8d76b68-v25v4           1/1     Running   0             12m
wordpress-mysql-5c5bf57bdb-bf8ww   1/1     Running   0             12m
```

once all of the pods are Running, we can proceed to the rolling update.

