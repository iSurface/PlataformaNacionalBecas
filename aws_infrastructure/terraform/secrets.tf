# AWS Secrets Manager para almacenar credenciales de BD y clave JWT
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "becas/backend/${var.environment}/secrets"
  recovery_window_in_days = 0

  tags = {
    Name = "becas-backend-secrets"
  }
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

resource "aws_secretsmanager_secret_version" "app_secrets_val" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    POSTGRES_SERVER   = aws_db_instance.postgres.address
    POSTGRES_PORT     = "5432"
    POSTGRES_USER     = var.db_username
    POSTGRES_PASSWORD = random_password.db_password.result
    POSTGRES_DB       = var.db_name
    JWT_SECRET_KEY    = random_password.jwt_secret.result
    DATABASE_URL      = "postgresql://${var.db_username}:${random_password.db_password.result}@${aws_db_instance.postgres.address}:5432/${var.db_name}"
  })
}
