import pulumi
import pulumi_aws as aws
import inspect
import re
from typing import Any, Dict

AWS_REGION_ABBREVIATIONS = {
    "us-east-1": "use1",
    "us-east-2": "use2",
    "us-west-1": "usw1",
    "us-west-2": "usw2",
    "af-south-1": "afs1",
    "ap-east-1": "ape1",
    "ap-south-1": "aps1",
    "ap-northeast-1": "apne1",
    "ap-northeast-2": "apne2",
    "ap-northeast-3": "apne3",
    "ap-southeast-1": "apse1",
    "ap-southeast-2": "apse2",
    "ca-central-1": "cac1",
    "eu-central-1": "euc1",
    "eu-west-1": "euw1",
    "eu-west-2": "euw2",
    "eu-west-3": "euw3",
    "eu-north-1": "eun1",
    "eu-south-1": "eus1",
    "me-south-1": "mes1",
    "sa-east-1": "sae1",
    "us-gov-east-1": "usge1",
    "us-gov-west-1": "usgw1",
    "cn-north-1": "cnn1",
    "cn-northwest-1": "cnnw1",
}

def to_snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def resolve_value(value: Any, resources: Dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {k: resolve_value(v, resources) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_value(item, resources) for item in value]
    elif isinstance(value, str):
        if value.startswith("secret:"):
            # Fetch secret from Pulumi config
            secret_key = value[len("secret:"):]
            config = pulumi.Config()
            return config.require_secret(secret_key)
        elif value.startswith("ref:"):
            ref_text = value[4:]
            if "." in ref_text:
                ref_res, ref_attr = ref_text.split(".", 1)
            else:
                ref_res, ref_attr = ref_text, "id"
            if ref_res not in resources:
                raise ValueError(f"Referenced resource '{ref_res}' not found.")
            resource_obj = resources[ref_res]
            attr_val = getattr(resource_obj, ref_attr, None)
            if attr_val is None:
                raise ValueError(f"Attribute '{ref_attr}' not found on resource '{ref_res}'")
            return attr_val
        else:
            return value
    else:
        return value

def get_lookup_params(required_params: set, resolved_args: dict) -> dict:
    lookup_params = {}
    for param in required_params:
        snake_key = to_snake_case(param)
        if snake_key in resolved_args:
            lookup_params[param] = resolved_args[snake_key]
        elif param in resolved_args:
            lookup_params[param] = resolved_args[param]
    return lookup_params

class AWSResourceBuilder:
    def __init__(self, config_data: dict):
        self.config = config_data
        self.resources: Dict[str, Any] = {}

    def get_abbreviation(self, region: str) -> str:
        return AWS_REGION_ABBREVIATIONS.get(region.lower(), region.split("-")[0].lower())

    def generate_resource_name(self, base_name: str) -> str:
        team = self.config.get("team", "team").strip().lower()
        service = self.config.get("service", "svc").strip().lower()
        env = self.config.get("environment", "dev").strip().lower()
        reg_abbr = self.get_abbreviation(self.config.get("region", "us-east-1"))
        return f"{team}-{service}-{env}-{reg_abbr}-{base_name}".lower()

    def resolve_args(self, args: dict) -> dict:
        return {key: resolve_value(value, self.resources) for key, value in args.items()}

    def _apply_common_parameters(self, resolved_args: dict, init_sig: inspect.Signature) -> dict:
        if "tags" in init_sig.parameters:
            resource_tags = self.config.get("tags")
            if resource_tags:
                resolved_args.setdefault("tags", resource_tags)
        else:
            resolved_args.pop("tags", None)
        if "region" in init_sig.parameters:
            if "region" not in resolved_args:
                resolved_args["region"] = self.config.get("region", "us-east-1")
        else:
            resolved_args.pop("region", None)
        return resolved_args

    def build(self):
        aws_resources = self.config.get("aws_resources", [])
        for resource_cfg in aws_resources:
            name = resource_cfg["name"]
            resource_type = resource_cfg["type"]
            args = resource_cfg.get("args", {}).copy()
            custom_name = resource_cfg.get("custom_name", None)
            is_existing = args.pop("existing", False)
            resolved_args = self.resolve_args(args)
            module_name, class_name = resource_type.rsplit(".", 1)
            module = getattr(aws, module_name, None)
            if not module:
                pulumi.log.warn(f"AWS module '{module_name}' not found. Skipping '{name}'.")
                continue
            try:
                ResourceClass = getattr(module, class_name)
            except AttributeError:
                pulumi.log.warn(f"Resource class '{class_name}' not found in module '{module_name}'. Skipping '{name}'.")
                continue
            init_sig = inspect.signature(ResourceClass.__init__)
            if is_existing:
                get_func_name = f"get_{to_snake_case(class_name)}"
                try:
                    get_func = getattr(module, get_func_name)
                    sig = inspect.signature(get_func)
                    get_required = {k for k, param in sig.parameters.items() if k not in {"opts"} and param.default == param.empty}
                    get_params = get_lookup_params(get_required, resolved_args)
                    missing = get_required - set(get_params.keys())
                    if missing:
                        pulumi.log.warn(f"Missing required params {missing} for existing resource '{name}'. Skipping the lookup attempt.")
                    else:
                        existing_resource = get_func(**get_params)
                        self.resources[name] = existing_resource
                        pulumi.log.info(f"Fetched existing resource '{name}' via '{get_func_name}' with {get_params}")
                        continue
                except AttributeError:
                    pulumi.log.warn(f"Function '{get_func_name}' not found for '{resource_type}'. Proceeding to create new resource '{name}'.")
                except Exception as e:
                    pulumi.log.warn(f"Failed to retrieve existing resource '{name}': {e}. Proceeding with creation.")
                if "region" in init_sig.parameters and "region" not in resolved_args:
                    resolved_args["region"] = self.config.get("region", "us-east-1")
                else:
                    resolved_args.pop("region", None)
            resolved_args = self._apply_common_parameters(resolved_args, init_sig)
            pulumi_name = custom_name if custom_name else self.generate_resource_name(name)
            pulumi.log.info(f"DEBUG for '{name}': final resolved_args => {resolved_args}")
            resource_instance = ResourceClass(pulumi_name, **resolved_args)
            self.resources[name] = resource_instance
            pulumi.log.info(f"Created resource: {pulumi_name} ({resource_type})")
