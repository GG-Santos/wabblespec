# Infrastructure as Code Standards

Loaded by Apply when gateway-engineering is active and Terraform or Pulumi files are detected.

## IaC requirements

All infrastructure must be declared in code. Console-created resources are not permitted in production environments — they are undocumented, unversioned, and not reproducible.

Spec must declare:
- **IaC tool**: Terraform, Pulumi, CDK, Bicep, CloudFormation
- **State backend**: where state is stored (Terraform Cloud, S3 + DynamoDB, Pulumi Cloud)
- **Workspace strategy**: how environments (dev/staging/prod) are managed
- **Module strategy**: what is shared across environments; what is environment-specific

## Terraform patterns

### Directory structure

```
infra/
  modules/          ← reusable modules (no state)
    networking/
      main.tf
      variables.tf
      outputs.tf
    database/
    compute/
  environments/     ← environment-specific configurations (have state)
    dev/
      main.tf       ← calls modules with dev-appropriate vars
      terraform.tfvars
      backend.tf    ← remote state config
    staging/
    prod/
```

### State management

```hcl
# backend.tf — remote state (required for teams)
terraform {
  backend "s3" {
    bucket         = "my-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"  # for state locking
  }
}
```

Rules:
- Remote state is required for all environments that teams share
- State locking prevents concurrent applies (DynamoDB lock for S3 backend)
- Never commit state files to source control — add `*.tfstate` to `.gitignore`

### Workspace strategy options

| Strategy | When |
|---|---|
| Separate state files per environment | Recommended — full isolation |
| Terraform workspaces | For simple cases; same module, different var values |
| Separate repositories | For strict compliance isolation |

### Sensitive variables

```hcl
# variables.tf
variable "db_password" {
  type      = string
  sensitive = true  # prevents value from appearing in plan/apply output
}

# Never put sensitive defaults here
# Pass via: TF_VAR_db_password env var, or -var file, or Vault provider
```

Secrets must come from a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault) — not from static var files.

### Plan review before apply

Required workflow:
```bash
terraform plan -out=plan.tfplan     # generates plan artifact
# Human reviews plan output
terraform apply plan.tfplan          # applies exactly the reviewed plan
```

In CI:
- PRs run `terraform plan` — output attached to PR for review
- Merge to main (or approval) triggers `terraform apply`
- Production apply requires manual approval gate

## State import and drift

Drift: infrastructure state differs from IaC definition.

```bash
# Check for drift
terraform plan  # no-op if no drift; shows changes if drift exists

# Import existing resource
terraform import aws_s3_bucket.my_bucket my-bucket-name
```

Spec must declare: process for importing existing resources; how drift is detected and resolved (automated reconcile vs manual).

## Module design rules

Modules must be:
- **Self-contained**: all resources needed for the feature declared inside
- **Parameterized**: environment-specific values passed via variables
- **Versioned**: modules pinned to a version when consumed (not floating `latest`)
- **Documented**: `variables.tf` with `description` on every variable; README with usage example

Anti-pattern: hard-coding environment names or account IDs inside modules.

## Breaking changes in IaC

Some Terraform operations are destructive:
- Renaming a resource = destroy + create (data loss for stateful resources)
- Changing a resource type = destroy + create
- Removing a resource = destroy

Before applying changes that involve destroy:
1. Verify the resource is safe to destroy (is data backed up? is this the right resource?)
2. Consider `terraform state mv` to rename without destroying
3. Use `lifecycle { prevent_destroy = true }` for critical resources

```hcl
resource "aws_rds_instance" "prod_db" {
  lifecycle {
    prevent_destroy = true  # terraform plan will error if this would be destroyed
  }
}
```
