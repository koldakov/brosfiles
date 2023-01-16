terraform {
  required_version = "~> 1.3"
}

resource "aws_secretsmanager_secret" "aws_secret_manager" {
  name                    = var.name
  description             = var.description
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "secret" {
  secret_id     = aws_secretsmanager_secret.aws_secret_manager.id
  secret_string = coalesce(var.value, random_string)
}

resource "random_string" "random_secret" {
  length  = var.random.length
  special = var.random.special
}

