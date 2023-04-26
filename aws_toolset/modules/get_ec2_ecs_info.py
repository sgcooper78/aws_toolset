import boto3, sys, argparse
from pprint import pprint

try:
    from utils import *
except ModuleNotFoundError:
    from .utils import *

def subparser_args_definitions(subparser):
    sub_subparser = subparser.add_parser('get_ec2_ecs_info', help='help for getting EC2 info from ecs')
    #required
    args_definitions(sub_subparser)

def args_definitions(parser):
    #required
    #optional
    parser.add_argument("--c","--cluster",default='', dest="Cluster",help="The Amazon Resource Name (ARN) or short name of the cluster the task is running in. If you do not specify a cluster, the default cluster is assumed.")
    parser.add_argument("--cn","--container-name",dest="ContainerName",help="Container name to give to filter by")
    parser.add_argument("--r","--region",dest="Region",help="The Region to use")
    parser.add_argument("--f","--full-output",dest="FullOutput", action='store_true',help="Option to give all details or not")

def list_clusters():
    paginator = ecs_client.get_paginator('list_clusters')

    all_resources_names = []
    for page in paginator.paginate():
        all_resources_names.extend(page["clusterArns"])

    return all_resources_names

def list_tasks(cluster):
    paginator = ecs_client.get_paginator('list_tasks')

    all_resources_names = []
    for page in paginator.paginate(cluster=cluster):
        all_resources_names.extend(page["taskArns"])

    return all_resources_names

def list_services(cluster):
    paginator = ecs_client.get_paginator('list_services')

    all_resources_names = []
    for page in paginator.paginate(cluster=cluster):
        all_resources_names.extend(page["serviceArns"])

    return all_resources_names

def list_tasks_with_containers(cluster,taskids):
    
    response = ecs_client.describe_tasks(
        cluster=cluster,
        tasks=taskids
    )
    container_names = {}
    for task in response['tasks']:
        task_id = task['taskArn']
        container_name = next(iter(task['containers']))['name']
        container_names[task_id] = {
            'task_id': task_id,
            'container_name': container_name
        }
    return container_names

def describe_services(cluster,services):
    
    response = ecs_client.describe_services(
        cluster=cluster,
        services=services
    )
    return response

def describe_task_container_name(cluster,taskid):
    
    response = ecs_client.describe_tasks(
        cluster=cluster,
        tasks=[
            taskid,
        ]
    )

    container_names = []
    for container in response['tasks'][0]['containers']:
        container_names.append(container['name'])
    return container_names

def describe_ec2_instances(instanceIds, ec2_client):
    
    response = ec2_client.describe_instances(
        InstanceIds=instanceIds
    )

    return response['Reservations'][0]['Instances']

def get_tasks(cluster,service_name):
    response = ecs_client.list_tasks(cluster=cluster, serviceName=service_name)
    tasks = response['taskArns']

    task_ids = []
    for task_arn in tasks:
        task_ids.append(task_arn.split("/")[-1])
    return task_ids

def run(args):
    if not args.Region:
        pprint("no region detected, using default profile region")
        args.Region = get_default_profile_region()
        pprint(args.Region)
    global ecs_client
    ecs_client = boto3.client('ecs', region_name=args.Region)
    if not args.Cluster:
        pprint("no user resource detected for cluster, helping user generate them")

        args.Cluster =  question_single_list(list_clusters(),"Cluster")
        
        pprint(f"{args.Cluster} has been chosen")
        if not args.Cluster:
            sys.exit("No Cluster detected")

    ec2_container_instances_arns = get_all_resource_names("ecs","ecs_container_instances",{"cluster" : args.Cluster})

    ec2_container_instances = ecs_client.describe_container_instances(
        cluster=args.Cluster,
        containerInstances=ec2_container_instances_arns
    )
    
    for instance in ec2_container_instances['containerInstances']:
            # Describe tasks
        instance['tasks'] = []
        instance['containerNames'] = []

        t_list_response = ecs_client.list_tasks(
            cluster=args.Cluster,
            containerInstance=instance['containerInstanceArn']
        )

        if not t_list_response['taskArns']:
            continue
        
        task_descriptions_response = ecs_client.describe_tasks(
            cluster=args.Cluster,
            tasks=t_list_response['taskArns']
        )
        instance['tasks'].append(task_descriptions_response)

        for task in task_descriptions_response['tasks']:
            for container in task["containers"]:
                instance['containerNames'].append(container["name"])
    

    if not args.ContainerName:
        pprint("no user resource detected for Container Name, helping user")


        containers = [container for instance in ec2_container_instances["containerInstances"] for container in instance["containerNames"]]
        
        if len(containers) != 1:
            args.ContainerName =  question_single_list(containers,"Container")
        else:
            pprint(f"Only one Container Detected, Container name {containers[0]} will be used")
            args.ContainerName = container[0]

        if not args.ContainerName:
            sys.exit("No container name detected")

    instances_with_target_container = [instance for instance in ec2_container_instances["containerInstances"] if args.ContainerName in instance["containerNames"]]

    ec2_client = boto3.client('ec2', region_name=args.Region)
    instance_ids = [instance["ec2InstanceId"] for instance in instances_with_target_container]
    instances_info = describe_ec2_instances(instance_ids,ec2_client)

    # pprint(instances_info)
    if args.FullOutput:
        pprint(instances_info)
    else:
        important_info = []
        for instance in instances_info:
            instance_info = {}
            instance_info["InstanceId"] = instance["InstanceId"]
            instance_info["InstanceType"] = instance["InstanceType"]
            instance_info["PrivateDnsName"] = instance["PrivateDnsName"]
            instance_info["PrivateIpAddress"] = instance["PrivateIpAddress"]
            instance_info["PublicDnsName"] = instance["PublicDnsName"]
            try:
                instance_info["PublicIpAddress"] = instance["PublicIpAddress"]
            except KeyError:
                pass

            # instance_info["NetworkInterfaces"] = instance["NetworkInterfaces"]

            important_info.append(instance_info)

        pprint(important_info)


def main():
    parser = argparse.ArgumentParser()

    args_definitions(parser)

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()