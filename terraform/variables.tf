variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance size"
  type        = string
  default     = "t2.micro"
}

variable "key_pair_name" {
  description = "Name of an existing EC2 key pair (for SSH access)"
  type        = string
}

variable "my_ip_cidr" {
  description = "Your IP in CIDR form, e.g. 1.2.3.4/32, so only you can SSH in"
  type        = string
}

variable "ghcr_repo" {
  description = "GitHub Container Registry repo path, e.g. sdeepaknetha/aiwaf"
  type        = string
}