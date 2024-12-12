# Rolling Update 

In general, this repository includes the contents of the files i used to perform a rolling update on the Wordpress application.

### Contents
- YAML Files
- Python Files
  -rolling update from 6.2.1 version to 6.3.1 version
  -rolling update from 6.1.1 version to 6.3.1 version

### How to set up environment for rolling update
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

### How to use execute rolling updates

first of all, there are two python codes included inside this repository.
  -rolling update from 6.2.1 version to 6.3.1 version
  -rolling update from 6.1.1 version to 6.3.1 version

the contents of the code is generally the same, the only thing different is the version of the wordpress application written in the wordpress-deployment.yaml file. below is an example of the version written in the file

```
        - name: WORDPRESS_DB_USER
          value: wordpress
        image: wordpress:6.2.1-apache
        imagePullPolicy: Always
        name: wordpress
        ports:
```
in the "name"part inside of the "spec" part of the deployment, the above is written. currently, the version is 6.2.1 but we will be updating the wordpress application to 6.3.1 by using the rollupdate_621_631.py code

the contents of the code is quite complicated to explain in detail, but i will be explaining the flow of the code below;
1. 
