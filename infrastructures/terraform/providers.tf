provider "aws" {
  region = var.region

  default_tags {
    tags = {
      CreatedBy = "terraform"
    }
  }
}
