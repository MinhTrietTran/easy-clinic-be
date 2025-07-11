import consul
import socket
import os
import time

def get_local_ip():
    """Lấy IP thực của container"""
    try:
        # Kết nối tới một địa chỉ bên ngoài để lấy IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def register_service():
    """Đăng ký service với Consul"""
    consul_host = os.environ.get('CONSUL_HOST', 'localhost')
    consul_port = int(os.environ.get('CONSUL_PORT', 8500))
    
    service_name = "medical_record_service"
    service_port = int(os.environ.get('SERVICE_PORT', 5000))  # Đổi từ 7000 thành 5000
    service_host = os.environ.get('SERVICE_HOST', get_local_ip())
    
    # Tạo Consul client
    c = consul.Consul(host=consul_host, port=consul_port)
    
    # Đăng ký service
    service_id = f"{service_name}-{service_host}-{service_port}"
    
    try:
        c.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=service_host,
            port=service_port,
            check=consul.Check.http(f"http://{service_host}:{service_port}/api/v1/health/", interval="10s"),
            tags=["medical", "django", "rest-api"]
        )
        print(f"✅ Service {service_name} registered successfully at {service_host}:{service_port}")
        
        # In thông tin đăng ký
        print(f"Service ID: {service_id}")
        print(f"Health Check: http://{service_host}:{service_port}/api/v1/health/")
        
    except Exception as e:
        print(f"❌ Failed to register service: {e}")
        # Không raise exception để service vẫn chạy được nếu Consul fail

if __name__ == "__main__":
    # Đợi một chút để đảm bảo network đã sẵn sàng
    time.sleep(2)
    register_service()