variable "value" {
  type = string
  default = null
}

variable "description" {
  type = string
  default = null
}

variable "random" {
  type = object({
    length  = number
    special = bool
  })

  default = {
    length = 24
    special = true
  }
}

variable "name" {
  type = string
}
