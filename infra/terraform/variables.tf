variable "inference_domain" {
  description = "The custom domain for the inference service, e.g., 'inference.example.com'."
  type        = string
}

variable "api_domain" {
  description = "The custom domain for the admin API service, e.g., 'api.example.com'."
  type        = string
}
