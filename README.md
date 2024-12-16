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
kubectl apply .k -n roll
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

once all of the pods are in the "Running" state, we can proceed to the rolling update.

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

1. deleting existing pods and deployments <br />
since the rolling update code will be used alot of times for data etc, the code will firstly delete all of the existing pods and deployments so that the version of the wordpress image could be set. the following commands will be used to delete it;

```
kubectl delete deployment wordpress -n roll
kubectl delete deployment wordpress-mysql -n roll
kubectl delete pods --all -n roll
```

2. replicas, maxSurge and maxUnavaliable inquiry
after deleting the existing pods and deployments, the code will then request the user to input the desired value for the 3 values stated. in the main function of the rolling update code, the following part of the code is the syntax for the stated function;
```
    replicas = int(input("Enter the number of replicas: "))
    max_surge = int(input("Enter the maxSurge value: "))
    max_unavailable = int(input("Enter the maxUnavailable value: "))
```

3. first deployment of wordpress application
after determining the three values stated above, the code will deploy the yaml files using the following command;
```
kubectl apply -f wordpress-deployment.yaml -n roll
```
this will deploy the wordpress deployment yaml file with the desired version (example, 6.2.1) 

4. rolling update
after the wordpress application with image version 6.2.1 is deployed, the code will then rewrite the image version to 6.3.1 so that the rolling update will be executed. the following code inside the main function is what edits the wordpress deployment file
```
    edit_yaml_file("6.3.1", replicas, max_surge, max_unavailable)
```

5. metrics records
after the rolling update is finished, the code will then record the time taken for the rolling update and alsothe average CPU usage during the rolling update.
below is an example of what will be shown on the terminal after the whole python code is finished executing.
```
myw@c0a22173-myw:~/roll$ python3 roll1.py
deployment.apps "wordpress" deleted
pod "wordpress-57fd86ff76-2qncg" deleted
pod "wordpress-57fd86ff76-2wvtc" deleted
pod "wordpress-57fd86ff76-4zfsq" deleted
pod "wordpress-57fd86ff76-65kkw" deleted
pod "wordpress-57fd86ff76-6865cl" deleted
pod "wordpress-57fd86ff76-7t22r" deleted
pod "wordpress-57fd86ff76-7t6kk" deleted
pod "wordpress-57fd86ff76-8hpt2" deleted
pod "wordpress-57fd86ff76-8md7m" deleted
pod "wordpress-57fd86ff76-8nl5p" deleted
pod "wordpress-57fd86ff76-bpwrp" deleted
pod "wordpress-57fd86ff76-h9d59" deleted
pod "wordpress-57fd86ff76-j6rml" deleted
pod "wordpress-57fd86ff76-jrwn7" deleted
pod "wordpress-57fd86ff76-pc8kd" deleted
pod "wordpress-57fd86ff76-pcc86" deleted
pod "wordpress-57fd86ff76-q6lt9" deleted
pod "wordpress-57fd86ff76-qdlq" deleted
pod "wordpress-57fd86ff76-wbjgr" deleted
Enter the number of replicas: 6
Enter the maxSurge value: 3
Enter the maxUnavailable value: 3
deployment.apps/wordpress created
6 containers are currently being deployed (expected max surge: 3).
0 out of 6 pods are running. Waiting...
All 6 pods are now running.
deployment.apps/wordpress configured
3 containers are currently being deployed (expected max surge: 3).
3 out of 6 pods are running. Waiting...
All 6 pods are now running.
Time taken for rolling update: 5.628972291946411 seconds
CPU Usage - Avg: 4.101449275362318m, Min: 1m, Max: 7m
Memory Usage - Avg: 13.0Mi, Min: 13Mi, Max: 13Mi
```
