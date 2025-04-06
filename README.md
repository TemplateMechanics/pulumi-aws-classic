# Pulumi YAML-Based Infrastructure Builder for AWS (Classic)

This project provides a dynamic and extensible Pulumi-based infrastructure-as-code solution for AWS, fully configured using a YAML file. It automatically manages resource naming, supports referencing existing resources, allows dynamic linking between resources, and can be versioned and reused as a Git component.

By leveraging YAML for configuration and a dynamic Python builder (named `awsclassic.py`), this solution abstracts the complexity of managing AWS resources. It paves the way for unified, multi-cloud operations by offering similar concepts across cloud providers—all accessible via open-source tooling.

---

## 📂 Project Structure

```
.
├── __main__.py         # Entry point: loads YAML and builds AWS resources
├── awsclassic.py       # AWS-specific logic and naming conventions
├── config.py           # Dataclasses and dynamic Pulumi resource mapping
├── config.yaml         # User-defined infrastructure configuration
└── README.md           # Documentation (this file)
```

---

## 🚀 Features

- **YAML-defined infrastructure:** Define all AWS resources clearly in YAML.
- **Dynamic Pulumi resource mapping:** No need to explicitly hardcode resource types.
- **Intelligent resource naming:** Automatically incorporates team, service, environment, and region abbreviations.
- **AWS region abbreviation:** Converts full AWS region names (e.g., `us-east-1`) into standardized abbreviations (`use1`).
- **Resource referencing:** Use `ref:<resource-name>.<attribute>` syntax to dynamically link resources.
- **New and existing resources:** Seamlessly create new resources or fetch existing ones from AWS.

---

## 📄 Example `config.yaml`

Below is an example configuration for AWS:

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
```

---

## 🛠 Getting Started

### Prerequisites

- [Pulumi](https://www.pulumi.com/docs/get-started/install/)
- AWS CLI (configured with your credentials)
- Python 3.7+ and dependencies from `requirements.txt`

### Setup Instructions

1. **Login to AWS CLI:**  
   ```bash
   aws configure
   ```
   This sets up your AWS credentials and default region.

2. **Login to Pulumi:**  
   ```bash
   pulumi login
   ```

3. **Initialize a New Pulumi Stack:**  
   ```bash
   pulumi stack init dev
   ```

4. **Set AWS Region (if required):**  
   ```bash
   pulumi config set aws:region us-east-1
   ```

5. **Deploy Your Infrastructure:**  
   ```bash
   pulumi up
   ```

---

## 🔗 Referencing Resources

Within your YAML file, you can use the syntax `ref:<resource-name>.<attribute>` to dynamically reference outputs from previously defined resources. This enables automatic dependency resolution.

**Example:**

```yaml
vpc_id: "ref:vpc-01.id"
```

This ensures that when the subnet is created, it correctly references the VPC created earlier.

---

## 🏷 Resource Naming Convention

Resource names are automatically generated following the pattern:

```
<team>-<service>-<environment>-<region-abbr>-<resource-name>
```

**Example:**

```
devops-test-svc-dev-use1-vpc-01
```

AWS region abbreviations (such as `us-east-1` → `use1`) are managed internally by the builder.

---

## ⚙️ Dynamic Resource Resolution

The system automatically introspects Pulumi’s AWS provider (`pulumi_aws`) to dynamically map resource types based on your YAML configuration. This dynamic mapping means you don't have to hardcode resource types—new resources added to the Pulumi AWS provider are automatically available. Key capabilities include:

- **Dynamic Resource Mapping:** Automatically find and instantiate the correct Pulumi resource classes.
- **Reference Resolution:** The builder resolves dependencies using the `ref:` syntax.
- **Common Parameter Injection:** Global configuration such as tags and region are automatically applied to resources that support them.
- **Lookup for Existing Resources:** Set an `existing` flag to fetch resources using lookup functions instead of creating them anew.

---

## ✨ Potential Enhancements

- **Reusable YAML Templates:** Create standardized templates for common resource patterns.
- **Multi-Region/Environment Support:** Expand the builder to manage multi-region or multi-environment deployments seamlessly.
- **Enhanced Dependency Visualization:** Integrate tools to visualize resource relationships.
- **Pre-Deployment YAML Validation:** Implement pre-execution checks to catch configuration errors early.

---

## 🌐 Unified Multi-Provider Strategy

While this project focuses on AWS, the approach is provider-agnostic. A similar YAML-driven infrastructure builder can be implemented for Azure, GCP, or any other cloud provider. The goal is to offer a consistent operational model with common APIs through open-source tooling.

Imagine maintaining a Git repository that houses versioned infrastructure components for AWS, Azure, and GCP. Teams could reference these components directly in their projects, ensuring standardized resource naming, dependency resolution, and operational practices across clouds.

This unified strategy simplifies cross-cloud operations, enabling organizations to:
- **Standardize Infrastructure Operations:** Use the same YAML configuration and resource builder logic for different clouds.
- **Enhance Collaboration:** Teams work with familiar configuration patterns and share best practices.
- **Leverage Open Source:** Build and contribute to community-driven components that serve as the foundation for consistent, multi-cloud infrastructure management.

---

## 👥 Authors & Contributors

This approach builds on the ideas pioneered by the **Benitez-Johnson Method** and has been developed and refined by:

- **Dave Johnson**
- **Christian Benitez**

Special thanks to **Brandon Rutledge** for architecture and implementation contributions.

---

Embrace the power of YAML and Pulumi to simplify, unify, and modernize your infrastructure management. By versioning these components and leveraging common APIs across cloud providers, you can create a robust, scalable, and maintainable infrastructure foundation for your organization.
