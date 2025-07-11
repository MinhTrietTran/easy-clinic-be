import consul  # type: ignore
import os
import socket

def register_to_consul():
    CONSUL_HOST = os.getenv('CONSUL_HOST', 'consul')
    CONSUL_PORT = int(os.getenv('CONSUL_PORT', 8500))

    SERVICE_NAME = 'notification_service'
    SERVICE_ID = 'notification_service'

    # Lấy IP thật của container
    SERVICE_ADDRESS = socket.gethostbyname(socket.gethostname())

    # FIX: Sửa port từ 5000 thành 7000 để match với dockerfile
    SERVICE_PORT = int(os.getenv('SERVICE_PORT', 7000))

    c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

    c.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=SERVICE_ADDRESS,
        port=SERVICE_PORT
    )

    print(f"[Consul] Registered {SERVICE_NAME} at {SERVICE_ADDRESS}:{SERVICE_PORT}")