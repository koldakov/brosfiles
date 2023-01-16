module "bf_engine_secret_key_secret" {
  source = "modules/aws_secret"
  name   = "BF/ENGINE/SECRET_KEY"
}

module "bf_db_psql_password_secret" {
  source = "modules/aws_secret"
  name   = "BF/DB/PSQL_PASSWORD"
}

module "bf_engine_jwt_auth_key_secret" {
  source = "modules/aws_secret"
  name   = "BF/ENGINE/JWT_AUTH_KEY"
}
