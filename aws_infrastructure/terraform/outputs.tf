output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.main.id
}

output "rds_endpoint" {
  description = "Endpoint de conexión para Amazon RDS PostgreSQL"
  value       = aws_db_instance.postgres.endpoint
}

output "alb_dns_name" {
  description = "URL pública del Application Load Balancer para acceder a la API"
  value       = "http://${aws_lb.main.dns_name}"
}

output "secrets_manager_arn" {
  description = "ARN del secreto en AWS Secrets Manager"
  value       = aws_secretsmanager_secret.app_secrets.arn
}
