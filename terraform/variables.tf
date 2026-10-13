variable "aws_region" {
  description = "AWS Region for the short-lived EKS demonstration."
  type        = string
  default     = "ap-southeast-2"
}

variable "cluster_name" {
  description = "Name shared by the VPC and EKS cluster."
  type        = string
  default     = "labpulse-capstone"
}

variable "availability_zones" {
  description = "Two available zones in the selected Region."
  type        = list(string)
  default     = ["ap-southeast-2a", "ap-southeast-2b"]

  validation {
    condition     = length(var.availability_zones) == 2 && var.availability_zones[0] != var.availability_zones[1]
    error_message = "Choose two distinct availability zones."
  }
}

variable "admin_cidr" {
  description = "Your public IP as a /32 CIDR, allowed to reach the EKS API."
  type        = string

  validation {
    condition     = can(cidrhost(var.admin_cidr, 0)) && var.admin_cidr != "0.0.0.0/0"
    error_message = "Use a valid restricted CIDR; do not expose the API to the whole internet."
  }
}

variable "node_instance_type" {
  description = "EC2 size for the managed node group."
  type        = string
  default     = "t3.small"
}

variable "offline_plan" {
  description = "Skip AWS identity checks for a local-only plan. Never apply with this enabled."
  type        = bool
  default     = false
}
