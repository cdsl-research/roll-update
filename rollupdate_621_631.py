import subprocess
import time
import yaml

def execute_command(command):
    """Helper function to execute shell commands and print output in real-time."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()

def edit_yaml_file(image_version, replicas, max_surge, max_unavailable):
    """Function to edit the YAML file with specified parameters."""
    yaml_file = "wordpress-deployment.yaml"
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    # Modify values
    data['spec']['replicas'] = replicas
    data['spec']['strategy']['rollingUpdate']['maxSurge'] = max_surge
    data['spec']['strategy']['rollingUpdate']['maxUnavailable'] = max_unavailable
    data['spec']['template']['spec']['containers'][0]['image'] = f"wordpress:{image_version}-apache"

    with open(yaml_file, 'w') as file:
        yaml.dump(data, file)

def wait_for_pods_ready(namespace, replicas, max_surge):
    """Waits until all pods are in the 'Running' state with all containers ready, and confirms deployment surge."""
    while True:
        result = subprocess.check_output(f"kubectl get pods -n {namespace}", shell=True, text=True)
        lines = result.splitlines()[1:]  # Skip header line
        running_pods = [line for line in lines if "1/1     Running" in line]
        creating_pods = [line for line in lines if "ContainerCreating" in line or "Pending" in line]

        # Display the number of containers creating at the same time
        if creating_pods:
            print(f"{len(creating_pods)} containers are currently being deployed (expected max surge: {max_surge}).")

        if len(running_pods) == replicas:
            print(f"All {replicas} pods are now running.")
            break
        
        print(f"{len(running_pods)} out of {replicas} pods are running. Waiting...")
        time.sleep(5)

def monitor_detailed_metrics(namespace):
    """Monitor CPU and memory usage, track min, max, and average usage during rolling update."""
    start_time = time.time()
    cpu_usages = []
    memory_usages = []

    while True:
        # Get pod CPU and memory usage
        try:
            result = subprocess.check_output(f"kubectl top pods -n {namespace}", shell=True, text=True)
            print(result)  # Print to monitor usage
            # Extract CPU and memory usage values
            for line in result.splitlines()[1:]:  # Skip header
                columns = line.split()
                cpu_usage = int(columns[1].replace("m", ""))  # Convert to milli-CPU
                memory_usage = int(columns[2].replace("Mi", ""))  # Memory in MiB

                cpu_usages.append(cpu_usage)
                memory_usages.append(memory_usage)
        except subprocess.CalledProcessError:
            print("Error in getting usage data. Ensure metrics-server is running.")
            break

        # Condition to break the loop when rolling update completes
        if check_rolling_update_complete(namespace):
            break
        time.sleep(5)

    end_time = time.time()
    total_time = end_time - start_time
    avg_cpu = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
    min_cpu = min(cpu_usages) if cpu_usages else 0
    max_cpu = max(cpu_usages) if cpu_usages else 0
    avg_memory = sum(memory_usages) / len(memory_usages) if memory_usages else 0
    min_memory = min(memory_usages) if memory_usages else 0
    max_memory = max(memory_usages) if memory_usages else 0

    return {
        "total_time": total_time,
        "cpu": {"avg": avg_cpu, "min": min_cpu, "max": max_cpu},
        "memory": {"avg": avg_memory, "min": min_memory, "max": max_memory},
    }

def check_rolling_update_complete(namespace):
    """Checks if all pods in the namespace are Running."""
    result = subprocess.check_output(f"kubectl get pods -n {namespace}", shell=True, text=True)
    return all("Running" in line for line in result.splitlines()[1:])  # Simple check for 'Running' status

def main():
    namespace = "roll"
    yaml_file = "wordpress-deployment.yaml"

    # Step 1: Delete existing deployments and pods
    execute_command(f"kubectl delete deployment wordpress -n {namespace}")
    execute_command(f"kubectl delete deployment wordpress-mysql -n {namespace}")
    execute_command(f"kubectl delete pods --all -n {namespace}")

    # Step 2: Prompt user for values and edit YAML file to set up initial deployment
    replicas = int(input("Enter the number of replicas: "))
    max_surge = int(input("Enter the maxSurge value: "))
    max_unavailable = int(input("Enter the maxUnavailable value: "))
    edit_yaml_file("6.2.1", replicas, max_surge, max_unavailable)

    # Step 3: Apply initial configuration
    execute_command(f"kubectl apply -f {yaml_file} -n {namespace}")
    # Wait until all replicas are in the Running state
    wait_for_pods_ready(namespace, replicas, max_surge)

    # Step 4: Modify YAML file to set up rolling update
    edit_yaml_file("6.3.1", replicas, max_surge, max_unavailable)

    # Step 5: Start rolling update and monitor it
    start_time = time.time()
    execute_command(f"kubectl apply -f {yaml_file} -n {namespace}")
    wait_for_pods_ready(namespace, replicas, max_surge)
    end_time = time.time()

    # Step 6: Collect detailed metrics
    rolling_update_time = end_time - start_time
    metrics = monitor_detailed_metrics(namespace)

    # Display results
    print(f"Time taken for rolling update: {rolling_update_time} seconds")
    print(f"CPU Usage - Avg: {metrics['cpu']['avg']}m, Min: {metrics['cpu']['min']}m, Max: {metrics['cpu']['max']}m")
    print(f"Memory Usage - Avg: {metrics['memory']['avg']}Mi, Min: {metrics['memory']['min']}Mi, Max: {metrics['memory']['max']}Mi")

if __name__ == "__main__":
    main()
