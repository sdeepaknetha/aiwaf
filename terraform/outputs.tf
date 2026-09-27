
output "public_ip" {
  value       = aws_instance.aiwaf.public_ip
  description = "Public IP of the AIWAF EC2 instance"
}

output "app_url" {
  value       = "http://${aws_instance.aiwaf.public_ip}:5000"
  description = "URL to access the deployed AIWAF app"
}