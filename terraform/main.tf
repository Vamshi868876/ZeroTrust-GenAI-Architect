# AWS Fargate Deployment for Zero-Trust RAG Engine

provider "aws" {
  region = "us-east-1"
}

resource "aws_ecs_cluster" "zerotrust_cluster" {
  name = "zerotrust-rag-engine-cluster"
}

resource "aws_ecs_task_definition" "backend_task" {
  family                   = "zerotrust-backend-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048

  container_definitions = jsonencode([
    {
      name      = "zerotrust-fastapi"
      image     = "your-ecr-repo/zerotrust-backend:latest"
      cpu       = 1024
      memory    = 2048
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "zerotrust_service" {
  name            = "zerotrust-backend-service"
  cluster         = aws_ecs_cluster.zerotrust_cluster.id
  task_definition = aws_ecs_task_definition.backend_task.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = ["subnet-12345678", "subnet-87654321"]
    security_groups  = ["sg-0123456789abcdef0"]
    assign_public_ip = true
  }
}
