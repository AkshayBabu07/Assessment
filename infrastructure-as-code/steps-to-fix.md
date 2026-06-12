# Steps to Fix: Removing the 2nd Resource from a `count`-based Resource Set
1. Identify current state addresses
```bash
terraform state list | grep aws_instance.example
```
Expected output:

aws_instance.example[0]
aws_instance.example[1]
aws_instance.example[2]
aws_instance.example[3]
aws_instance.example[4]

2. Update the configuration: convert `count` to `for_each`

locals {
  instance_keys = toset(["0", "2", "3", "4"])
}

resource "aws_instance" "example" {
  for_each = local.instance_keys

  ami           = "ami-id"
  instance_type = "t3.micro"

  tags = {
    Name = "instance-${each.value}"
  }
}

3. Re-map existing state entries to the new `for_each` addresses

Move state for every resource you want to KEEP:

```bash
terraform state mv 'aws_instance.example[0]' 'aws_instance.example["0"]'
terraform state mv 'aws_instance.example[2]' 'aws_instance.example["2"]'
terraform state mv 'aws_instance.example[3]' 'aws_instance.example["3"]'
terraform state mv 'aws_instance.example[4]' 'aws_instance.example["4"]'
```

Do NOT move `aws_instance.example[1]` — leaving it unmapped means it has no
corresponding entry in the new `for_each` configuration and will be destroyed.

4. (Optional) Remove from state instead of destroying

terraform state rm 'aws_instance.example[1]'

5. Validate the plan

terraform plan

Expected result:
- `aws_instance.example[1]` is planned for destruction (one-time).
- All other resources (now `["0"]`, `["2"]`, `["3"]`, `["4"]`) show **no changes**.

6. Apply the change


terraform apply

This destroys only the 2nd resource; the rest remain untouched.

7. Verify idempotency

terraform apply

Expected output: **"No changes. Your infrastructure matches the configuration."**