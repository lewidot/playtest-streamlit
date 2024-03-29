"""Functions to produce the cli arguments for pytest."""


def generate_cli_args(config: dict, path: str) -> list:
    """Return a list of string arguments for the pytest.main() call."""
    cli_args = []

    if config["headed"]:
        cli_args.append("--headed")

    if config["verbose"]:
        cli_args.append("-v")

    if config["test_dir"] is not None:
        cli_args.append(config["test_dir"])
    elif config["test_file"] is not None:
        cli_args.append(config["test_file"])
    elif config["test_case"] is not None:
        cli_args.append(config["test_case"])
    else:
        cli_args.append("tests")

    if config["marks"]:
        cli_args.append("-m")
        cli_args.append(" or ".join([str(m) for m in config["marks"]]))

    if config["playtest-report"]:
        cli_args.append("--playtest-report")
        cli_args.append(path)

    if config["parallel"]:
        cli_args.append("--numprocesses")
        cli_args.append("auto")

    if config["rerun"] > 0:
        cli_args.append("--reruns")
        cli_args.append(str(config["rerun"]))

    if config["tracing"]:
        cli_args.append("--tracing")
        cli_args.append("on")
        cli_args.append("--output")
        cli_args.append(path)

    return cli_args
