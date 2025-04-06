# Pulumi YAML-Based Infrastructure Builder for AWS (Classic)

This project provides a dynamic and extensible Pulumi-based infrastructure-as-code solution for AWS, fully configured using a YAML file. It automatically manages resource naming (with custom name overrides), supports referencing existing resources, allows dynamic linking between resources, and integrates secret resolution via Pulumi configuration. It can be versioned and reused as a Git component.

## 📂 Project Structure

```
.
├── __main__.py         # Entry point: loads YAML and builds AWS resources
├── awsclassic.py       # AWS-specific logic, naming conventions, and secret resolution
├── config.py           # Dataclasses and dynamic Pulumi resource mapping
├── config.yaml         # User-defined infrastructure configuration
└── README.md           # Documentation (this file)
```

---

## 🚀 Features

- **YAML-defined infrastructure**: Define all infrastructure clearly in YAML.
- **Dynamic Pulumi resource mapping**: Automatically maps YAML definitions to Pulumi resource classes.
- **Intelligent resource naming**: Automatically incorporates team, service, environment, and region abbreviations.
- **AWS region abbreviation**: Converts full AWS region names (e.g., `us-east-1`) into standardized abbreviations (e.g., `use1`).
- **Resource referencing**: Use `ref:<resource-name>.<attribute>` syntax to dynamically link resources.
- **New and existing resources**: Seamlessly create new resources or fetch existing ones.
- **Custom name overrides**: Override generated names with a `custom_name` field for resources with strict naming rules.
- **Secret resolution**: Use `secret:<key>` in your YAML to securely reference sensitive data from Pulumi configuration.

---

## 📄 Example `config.yaml`

```yaml
team: "DevOps"
service: "test-svc"
environment: "dev"
region: "us-east-1"
tags:
  owner: "test-user"
  project: "PulumiTest"

aws_resources:
  - name: "vpc-01"
    type: "ec2.Vpc"
    args:
      cidr_block: "10.0.0.0/16"
      tags:
        Name: "vpc-01"

  - name: "existing-vpc"
    type: "ec2.Vpc"
    args:
      existing: true
      vpc_id: "vpc-0abc12345def67890"  # Replace with an actual VPC ID

  - name: "subnet-01"
    type: "ec2.Subnet"
    args:
      vpc_id: "ref:vpc-01.id"
      cidr_block: "10.0.1.0/24"
      availability_zone: "us-east-1a"

  - name: "ec2-instance"
    type: "ec2.Instance"
    custom_name: "myinstance"  # Custom override for resources with naming restrictions
    args:
      ami: "ami-0abcdef1234567890"
      instance_type: "t2.micro"
      key_name: "secret:awsKeyPairName"
```

---

## 🛠 Getting Started

```bash
aws configure
pulumi login
pulumi stack init dev
pulumi config set aws:region us-east-1
pulumi config set awsKeyPairName YOUR_KEY_PAIR_NAME --secret
pulumi up
```

---

## 🔗 Referencing Resources

Use the syntax `ref:<resource-name>.<attribute>` to dynamically reference outputs from previously defined resources.

Example:

```yaml
vpc_id: "ref:vpc-01.id"
```

---

## 🏷 Resource Naming Convention

Resource names follow the pattern:

```
<team>-<service>-<environment>-<region-abbr>-<resource-name>
```

**Example:**

```
devops-test-svc-dev-use1-vpc-01
```

---

## ⚙️ Dynamic Resource Resolution

The system automatically introspects Pulumi AWS packages (`pulumi_aws`) to dynamically map resources without explicit resource class definitions, simplifying management and ensuring new resources are available as Pulumi updates.

---

## ✨ Potential Enhancements

- **Reusable YAML templates** for common resource patterns.
- **Multi-region and multi-environment support**.
- **Enhanced dependency visualization**.
- **Pre-execution YAML validation**.

---

## 👥 Authors & Contributors

Developed using the **Benitez-Johnson Method** by:
- **Dave Johnson**
- **Christian Benitez**

Special thanks to **Brandon Rutledge** for architecture and implementation contributions.
