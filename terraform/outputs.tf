output "cluster_name" {
  value = aws_eks_cluster.labpulse.name
}

output "cluster_endpoint" {
  value = aws_eks_cluster.labpulse.endpoint
}

output "vpc_id" {
  value = aws_vpc.labpulse.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "configure_kubectl" {
  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.labpulse.name}"
}
