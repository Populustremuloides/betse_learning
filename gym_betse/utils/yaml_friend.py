import yaml
import os
import pandas as pd
import numpy as np

EXTRA_CONFIGS = "extra_configs"

def extract_params_recursive(config, param_path, prefix=""):
    """
    Recursively extracts parameters from a nested dictionary or list based on a parameter path.
    - If a list is encountered, it searches for a "name" field in the list elements.
    - Appends the value of "name" to the key if found, otherwise defaults to an index-based key.
    """
    if not param_path:
        return {prefix: config}  # Base case: end of path

    key = param_path[0]
    remaining_path = param_path[1:]
    extracted = {}

    if isinstance(config, dict):
        if key in config:
            extracted.update(extract_params_recursive(config[key], remaining_path, prefix))
    elif isinstance(config, list):
        # append the key back to the beginning of the remaining path
        remaining_path.insert(0, key)
        for item in config:
            if isinstance(item, dict) and "name" in item:
                # Use the "name" field if available
                item_prefix = f"{prefix}_{item['name']}" if prefix else f"{key}_{item['name']}"
                if not remaining_path:
                    return {item_prefix: item[key]}
            else:
                # Fallback to index if "name" is not found
                index = config.index(item)
                item_prefix = f"{prefix}_{index}" if prefix else f"{key}_{index}"
            extracted.update(extract_params_recursive(item, remaining_path, item_prefix))
    return extracted

def extract_params(params, config_path, params_to_extract):
    """
    Extracts desired parameters from YAML files and saves them to a dictionary.
    """
    # Load the main YAML configuration
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return params

    # Attempt to load the GRN config if specified
    grn_config = None
    grn_config_path = config.get("gene regulatory network settings", {}).get("gene regulatory network config")
    if grn_config_path:
        if not os.path.isabs(grn_config_path):
            grn_config_path = os.path.join(os.path.dirname(config_path), grn_config_path)
        try:
            with open(grn_config_path, 'r') as file:
                grn_config = yaml.safe_load(file)
        except Exception as e:
            print(f"Error reading GRN config {grn_config_path}: {e}")

    # Extract parameters
    for param in params_to_extract:
        if "ID" in param:
            params[param].append(os.path.basename(os.path.dirname(config_path)))
            continue

        param_parts = param.split("/")
        filetype = param_parts.pop(0)

        source_config = config if filetype == "config" else grn_config
        if source_config is None:
            params[param].append(None)
            continue

        extracted = extract_params_recursive(source_config, param_parts, param)
        for key, value in extracted.items():
            if key not in params:
                params[key] = []
                # Fill with None for previous entries
                params[key].extend([None] * len(params[param]))
            params[key].append(value)

    return params


def get_param_list(params_to_extract):
    """
    :param params_to_extract: Text file with newline-separated parameter paths.
    :return: List of parameters extracted from file.
    """
    with open(params_to_extract, 'r') as file:
        params = [line.strip() for line in file]
        # remove "" if it exists
        if "" in params:
            params.remove("")
    return params


def create_params_dataset(directory_to_analyze, params_to_extract=None, save_param_path=None):
    """
    Creates a pandas DataFrame with parameters extracted from YAML files.
    """
    if params_to_extract is None:
        params_to_extract = [
            "ID",
            "config/tissue profile definition/tissue/default/diffusion constants/Dm_Cl",
            "config/tissue profile definition/tissue/default/diffusion constants/Dm_Na",
            "config/tissue profile definition/tissue/default/diffusion constants/Dm_K",
            "config/tissue profile definition/tissue/default/diffusion constants/Dm_Ca",
            "config/variable settings/gap junctions/gap junction surface area",
            "config/variable settings/gap junctions/gj minimum",
            "config/variable settings/gap junctions/gj voltage threshold",
            "grn/biomolecules/Dgj",
            "grn/biomolecules/cell conc",
            "grn/biomolecules/growth and decay/decay rate",
            "grn/biomolecules/growth and decay/production rate",
            "grn/biomolecules/z",
        ]
    else:
        params_to_extract = get_param_list(params_to_extract)

    params_dict = {param: [] for param in params_to_extract}
    for root, dirs, files in os.walk(directory_to_analyze):
        if "extra_configs" in root:
            continue
        for file in files:
            if file.endswith(".yaml"):
                config_path = os.path.join(root, file)
                params_dict = extract_params(params_dict, config_path, params_to_extract)
                # see if any lists were not updated (size max - 1) and fill with None
                max_len = max(len(v) for v in params_dict.values())
                for k, v in params_dict.items():
                    if len(v) < max_len:
                        params_dict[k].extend([None] * (max_len - len(v)))

    # remove all keys with all None values
    params_dict = {k: v for k, v in params_dict.items() if any(x is not None for x in v)}

    # remove dict item with key name "" if it exists
    if "" in params_dict:
        params_dict.pop("")

    df = pd.DataFrame(params_dict)
    df.to_csv("Physiology/params_initial_values.csv")

    if save_param_path:
        with open(save_param_path, 'w') as file:
            for key in params_dict.keys():
                file.write(f"{key}\n")


def gather_initial_values(values_csv, params_list):
    """
    :param values_csv: Path to CSV file containing initial values.
    :param params_list: List of parameter paths to extract from the CSV.
    :return: List of initial values corresponding to the parameter paths.
    """
    df = pd.read_csv(values_csv)
    return [df[param].iloc[0] for param in params_list]


def update_yaml_from_paths(file_path, paths, values, write_path=None):
    """
    Updates a YAML file at specified paths with the given values.

    :param file_path: Path to the YAML file to update.
    :param paths: List of parameter paths to update in the YAML structure.
    :param values: List of corresponding values to assign to each parameter path.
    """
    if len(paths) != len(values):
        raise ValueError("Paths and values must have the same length.")

    def update_recursive(config, param_path, value):
        """
        Recursively updates the YAML structure at the given path with the value.
        """
        key = param_path[0]
        remaining_path = param_path[1:]

        # Handle case where we are dealing with a list
        if isinstance(config, list):
            # put the key back at the beginning of the remaining path
            remaining_path.insert(0, key)

            # Extract name from key if present
            if "_" in remaining_path[-1]:
                _, name_suffix = remaining_path[-1].split("_", 1)
            else:
                raise ValueError(f"Key '{key}' does not specify a target name in a list.")

            # Find the element in the list with the matching "name" field
            for item in config:
                if isinstance(item, dict) and item.get("name") == name_suffix:
                    update_recursive(item, remaining_path, value)
                    return

            # If no matching "name" field is found, raise an error
            raise KeyError(f"No list element with 'name' matching '{name_suffix}' found.")

        # Handle case where we are dealing with a dictionary
        elif isinstance(config, dict):

            # handle case where key is not in the config (maybe because we changed the name)
            if key not in config:
                if "_" in key:
                    key, _ = key.split("_", 1)
                else:
                    raise KeyError(f"Key '{key}' not found in the configuration.")

            if remaining_path:
                update_recursive(config[key], remaining_path, value)
            else:
                config[key] = value  # Base case: assign the value

        else:
            raise TypeError(f"Unexpected type {type(config)} encountered while traversing.")

    # Load the YAML file
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file) or {}
    except Exception as e:
        raise RuntimeError(f"Failed to read YAML file '{file_path}': {e}")

    # Update the paths
    for path, value in zip(paths, values):
        param_path = path.split("/")
        if param_path[0] == "config":
            param_path.pop(0)

        if param_path[0] == "grn":
            param_path.pop(0)
            if "gene regulatory network settings" not in config:
                config["gene regulatory network settings"] = {}
            if "gene regulatory network config" not in config["gene regulatory network settings"]:
                config["gene regulatory network settings"]["gene regulatory network config"] = {}
            update_recursive(config["gene regulatory network settings"]["gene regulatory network config"], param_path, value)

        update_recursive(config, param_path, value)

    # Save the updated YAML file
    if write_path is None:
        write_path = file_path
    try:
        with open(write_path, 'w') as file:
            yaml.dump(config, file)
    except Exception as e:
        raise RuntimeError(f"Failed to write updated YAML file '{write_path}': {e}")


def perturb_values(values):
    """
    Perturbs the given values by up to 200% of the magnitude of the value in either direction.
    """
    new_vals = [value + (np.random.uniform(-0.5, 0.5) * value) for value in values]
    # truncate floats to 2 significant figures
    new_vals = [f"{x:.2e}" for x in new_vals]
    return [float(x) for x in new_vals]