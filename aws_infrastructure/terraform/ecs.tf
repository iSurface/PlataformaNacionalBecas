# Security Group para el Backend
resource "aws_security_group" "backend" {
  name        = "becas-sg-backend-${var.environment}"
  description = "Permite trafico entrante desde el ALB en el puerto 8000"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP desde el ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "becas-sg-backend"
  }
}

# Security Group para el Application Load Balancer (Público)
resource "aws_security_group" "alb" {
  name        = "becas-sg-alb-${var.environment}"
  description = "Permite trafico HTTP/HTTPS desde Internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP desde Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS desde Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "becas-sg-alb"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "becas-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  tags = {
    Name = "becas-alb"
  }
}

# Target Group para ECS
resource "aws_lb_target_group" "app" {
  name        = "becas-tg-${var.environment}"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

# Listener HTTP para el ALB
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Amazon ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "becas-cluster-${var.environment}"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/becas-backend-${var.environment}"
  retention_in_days = 30
}

# IAM Role para ECS Task Execution
resource "aws_iam_role" "ecs_execution" {
  name = "becas-ecs-task-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "ecs_secrets" {
  name        = "becas-ecs-secrets-policy-${var.environment}"
  description = "Permite a ECS leer credenciales de AWS Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [aws_secretsmanager_secret.app_secrets.arn]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_attach" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = aws_iam_policy.ecs_secrets.arn
}

# ECS Task Definition para Fargate
resource "aws_ecs_task_definition" "app" {
  family                   = "becas-backend-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn

  container_definitions = jsonencode([{
    name      = "becas-backend"
    image     = var.container_image
    essential = true
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
    }]
    secrets = [
      {
        name      = "POSTGRES_SERVER"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:POSTGRES_SERVER::"
      },
      {
        name      = "POSTGRES_PORT"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:POSTGRES_PORT::"
      },
      {
        name      = "POSTGRES_USER"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:POSTGRES_USER::"
      },
      {
        name      = "POSTGRES_PASSWORD"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:POSTGRES_PASSWORD::"
      },
      {
        name      = "POSTGRES_DB"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:POSTGRES_DB::"
      },
      {
        name      = "JWT_SECRET_KEY"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:JWT_SECRET_KEY::"
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "backend"
      }
    }
  }])
}

# ECS Service Fargate
resource "aws_ecs_service" "app" {
  name            = "becas-service-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_app_a.id, aws_subnet.private_app_b.id]
    security_groups  = [aws_security_group.backend.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "becas-backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}
