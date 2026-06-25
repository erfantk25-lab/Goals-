variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "environment" { type = string }
variable "project_name" { type = string }
variable "vnet_address_space" { type = string }
variable "app_subnet_prefix" { type = string }
variable "db_subnet_prefix" { type = string }
variable "tags" { type = map(string) }
