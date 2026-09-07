variable "aws_region" {
  description = "Región de AWS para el despliegue"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de ejecución (development, staging, production)"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "Bloque CIDR para la VPC institucional"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_name" {
  description = "Nombre de la base de datos PostgreSQL"
  type        = string
  default     = "becas_db"
}

variable "db_username" {
  description = "Usuario administrador de Amazon RDS PostgreSQL"
  type        = string
  default     = "becas_admin"
}

variable "container_image" {
  description = "URI de la imagen Docker en Amazon ECR"
  type        = string
  default     = "688886174570.dkr.ecr.us-east-1.amazonaws.com/becas-backend:latest"
}
