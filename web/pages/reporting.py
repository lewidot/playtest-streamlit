"""Streamlit page for accessing and viewing reports."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import json  # noqa: E402

import streamlit as st  # noqa: E402

from utils.list_paths import list_json_report_files  # noqa: E402


def path_parent(path: Path) -> str:
    """Get the parent folder from a file path."""
    parent = path.parent
    return parent.stem


def load_json_report(file: Path) -> dict:
    """Load a json report."""
    try:
        with open(report_path) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        err = f"Report file: {file} does not exist."
        print(err)


def get_unique_tests(data: dict) -> tuple[str]:
    """Get all unique node ids from json report."""
    return tuple(set([x["nodeid"] for x in data]))


def get_total_duration(data: dict) -> float:
    """Get total duration from json report."""
    # Get total duration from the metadata object
    metadata = data.get("metadata")
    duration = metadata[1].get("total_duration")
    return duration


def get_results_count(data: dict) -> int:
    """Get the number of tests passed and failed from the json report."""
    # Identify the test data object
    test_data = data.get("test_data")

    # Initialise counters
    passed_count = 0
    failed_count = 0

    # Get number of passed outcomes and increment counter
    for test in test_data:
        if test["when"] == "call":
            if test["outcome"] == "passed":
                passed_count += 1
            else:
                failed_count += 1

    return passed_count, failed_count


def parse_test_results(data: dict, test_cases: tuple[str]) -> list[dict]:
    """Parse the json report for results to pass into a dataframe."""
    # Identify the test data object
    test_data = data.get("test_data")

    # Initialise empty results list
    results = []

    # Get each object for each unique nodeid
    for test in test_cases:
        test_results = {"Test Case": test}
        test_objects = [x for x in test_data if x["nodeid"] == test]
        for test_object in test_objects:
            if test_object["when"] == "call":
                outcome = test_object["outcome"]
                call_duration = test_object["duration"]
            elif test_object["when"] == "setup":
                setup_duration = test_object["duration"]

            elif test_object["when"] == "teardown":
                teardown_duration = test_object["duration"]

        total_duration = call_duration + setup_duration + teardown_duration
        test_results.update(
            {
                "Outcome": outcome,
                "Setup Duration": round(setup_duration, 2),
                "Call Duration": round(call_duration, 2),
                "Teardown Duration": round(teardown_duration, 2),
                "Total Duration": round(total_duration, 2),
            }
        )

        results.append(test_results)

    return results


st.set_page_config(
    page_title="Reports",
    page_icon="random",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title(body="Reports")

report_col1, report_col2 = st.columns(2)

# Select a date to filter selectable test reports
with report_col1:
    selected_date = st.date_input(label="Select a date").strftime("%d-%m-%Y")

with report_col2:
    # Select a json report, formatted to show only parent folder
    report_path = st.selectbox(
        label="Available reports",
        options=list_json_report_files(date=selected_date),
        format_func=path_parent,
    )


view_report = st.button(label="View Report", type="primary")

if report_path is not None and view_report:
    st.write(f"Selected report: {report_path}")

    # Load json report into a dict
    data = load_json_report(file=report_path)

    # Get the test data object from the report
    test_data = data.get("test_data")

    # Get all unique node ids from the test cases
    test_cases = get_unique_tests(test_data)

    # Get count of passed and failed test results
    passed_count, failed_count = get_results_count(data=data)

    st.subheader(body="Test Run Summary")

    info_col1, info_col2, info_col3, info_col4 = st.columns(4)

    # Display the total test run duration
    with info_col1:
        st.info(body=f"Total duration: {get_total_duration(data=data)}s", icon="⏰")

    # Display total number of tests
    with info_col2:
        st.info(body=f"Number of tests: {len(test_cases)}", icon="🧮")

    # Display number of tests passed
    with info_col3:
        st.success(body=f"Passed: {passed_count}", icon="✅")

    # Display number of tests failed
    with info_col4:
        st.error(body=f"Failed: {failed_count}", icon="❌")

    st.dataframe(
        data=parse_test_results(data=data, test_cases=test_cases),
        use_container_width=True,
    )

    # Display the raw json
    with st.expander(label="Raw json report data"):
        st.json(data)
