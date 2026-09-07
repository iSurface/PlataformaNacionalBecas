# Grupo de Subredes para RDS
resource "aws_db_subnet_group" "rds" {
  name       = "becas-rds-subnet-group-${var.environment}"
  subnet_ids = [aws_subnet.private_db_a.id, aws_subnet.private_db_b.id]

  tags = {
    Name = "becas-db-subnet-group"
  }
}

# Security Group para RDS PostgreSQL
resource "aws_security_group" "rds" {
  name        = "becas-sg-rds-${var.environment}"
  description = "Permite acceso exclusivo al puerto 5432 desde el backend"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL desde el Security Group del Backend"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "becas-sg-rds"
  }
}

# Generación aleatoria de contraseña segura para RDS
resource "random_password" "db_password" {
  length  = 32
  special = false
}

# Instancia de Amazon RDS for PostgreSQL 15
resource "aws_db_instance" "postgres" {
  identifier             = "becas-rds-${var.environment}"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "postgres"
  engine_version         = "16.3"
  auto_minor_version_upgrade = true
  instance_class         = "db.t4g.micro"
  db_name                = var.db_name
  username               = var.db_username
  password               = random_password.db_password.result
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  multi_az               = false  # Set to true for Multi-AZ in prod
  skip_final_snapshot    = true
  storage_encrypted      = true
  publicly_accessible    = false
  backup_retention_period = 7

  tags = {
    Name = "becas-rds-postgresql"
  }
}
