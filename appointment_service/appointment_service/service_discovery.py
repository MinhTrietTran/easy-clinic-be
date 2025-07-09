import consul # type: ignore

def get_service_address(service_name, consul_host="consul", consul_port=8500):
    c = consul.Consul(host=consul_host, port=consul_port)
    index, nodes = c.health.service(service_name, passing=True)
    if nodes:
        node = nodes[0]
        address = node['Service']['Address']
        port = node['Service']['Port']
        return address, port
    raise Exception("Service not found or not healthy")

def is_service_alive(service_name, consul_host="consul", consul_port=8500):
    c = consul.Consul(host=consul_host, port=consul_port)
    index, nodes = c.health.service(service_name, passing=True)
    return bool(nodes)

# Trường hợp loadblancing khi có nhiều instance cùng service_name
# def get_all_service_instances(service_name, consul_host="consul", consul_port=8500):
#     c = consul.Consul(host=consul_host, port=consul_port)
#     index, nodes = c.health.service(service_name, passing=True)
#     return [
#         (node['Service']['Address'], node['Service']['Port'])
#         for node in nodes
#     ]

# import random
# def get_random_service_instance(service_name, consul_host="consul", consul_port=8500):
#     instances = get_all_service_instances(service_name, consul_host, consul_port)
#     if not instances:
#         raise Exception("No healthy instances found")
#     return random.choice(instances)



