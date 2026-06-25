variable "environment" {
  type        = string
  description = "The environment name (e.g., dev, staging, prod)"
}

variable "project_name" {
  type        = string
  description = "The project name"
}

variable "location" {
  type        = string
  description = "The Azure region"
}

variable "vnet_address_space" {
  type        = string
  description = "VNet address space"
}

variable "app_subnet_prefix" {
  type        = string
  description = "Subnet prefix for container apps"
}

variable "db_subnet_prefix" {
  type        = string
  description = "Subnet prefix for database"
}

variable "db_admin_username" {
  type        = string
  description = "PostgreSQL admin username"
}

variable "db_name" {
  type        = string
  description = "Name of the initial PostgreSQL database"
}

variable "image_name" {
  type        = string
  description = "The name of the docker image"
}

variable "image_tag" {
  type        = string
  description = "The tag of the docker image"
}
