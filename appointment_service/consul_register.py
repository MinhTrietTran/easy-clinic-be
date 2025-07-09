import consul # type: ignore
import os

def register_to_consul():
    CONSUL_HOST = os.getenv('CONSUL_HOST', 'consul')
    CONSUL_PORT = int(os.getenv('CONSUL_PORT', 8500))

    SERVICE_NAME = 'appointment_service'
    SERVICE_ID = 'appointment_service_1'
    SERVICE_ADDRESS = os.getenv('SERVICE_HOST', 'appointment_service')  # service name trong docker-compose
    SERVICE_PORT = int(os.getenv('SERVICE_PORT', 5000))  # port nội bộ container

    c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

    c.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=SERVICE_ADDRESS,
        port=SERVICE_PORT
    )

    print(f"[Consul] Registered {SERVICE_NAME} at {SERVICE_ADDRESS}:{SERVICE_PORT}")

if __name__ == "__main__":
    register_to_consul()