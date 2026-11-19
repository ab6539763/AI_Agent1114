"""
Day 56 课后作业 1（基础巩固）：基础巩固：生成带健康检查依赖的 docker-compose.yml
工单：STARMIND-056
"""

from src.day56_deploy_generator import DeploySpec


def render_docker_compose(spec: DeploySpec) -> str:
    return f"""services:
  {spec.app_name}:
    build: .
    restart: unless-stopped
    env_file: .env
    networks: [starmind-net]
  nginx:
    image: nginx:1.27-alpine
    ports: ["{spec.nginx_port}:80"]
    volumes: ["./nginx.conf:/etc/nginx/conf.d/default.conf:ro"]
    depends_on:
      {spec.app_name}:
        condition: service_healthy
    networks: [starmind-net]
networks:
  starmind-net:
    driver: bridge
"""


print(render_docker_compose(DeploySpec()))

