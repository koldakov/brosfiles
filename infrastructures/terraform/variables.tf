variable "project_name" {
  description = "Project name"
  type        = string
}

variable "region" {
  description = "The AWS region to create resources in."
  type        = string
}


variable "postgresql_port" {
  description = "Postgresql port"
  type        = string
}

variable "allowed_hosts" {
  description = "Django allowed hosts"
  type        = string
}

variable "debug" {
  description = "Debug mode"
  type        = bool
}
