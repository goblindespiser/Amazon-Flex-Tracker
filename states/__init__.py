from . import california, florida, illinois, new_york, north_carolina, ohio, pennsylvania, texas, virginia

STATE_MODULES = {
    ohio.STATE_CODE: {
        "name": ohio.STATE_NAME,
        "calculate": ohio.calculate_ohio_tax,
        "field_labels": ohio.STATE_FIELD_LABELS,
        "estimate_label": ohio.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": ohio.STATE_TAX_FRAME_TITLE,
    },
    california.STATE_CODE: {
        "name": california.STATE_NAME,
        "calculate": california.calculate_california_tax,
        "field_labels": california.STATE_FIELD_LABELS,
        "estimate_label": california.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": california.STATE_TAX_FRAME_TITLE,
    },
    texas.STATE_CODE: {
        "name": texas.STATE_NAME,
        "calculate": texas.calculate_texas_tax,
        "field_labels": texas.STATE_FIELD_LABELS,
        "estimate_label": texas.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": texas.STATE_TAX_FRAME_TITLE,
    },
    florida.STATE_CODE: {
        "name": florida.STATE_NAME,
        "calculate": florida.calculate_florida_tax,
        "field_labels": florida.STATE_FIELD_LABELS,
        "estimate_label": florida.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": florida.STATE_TAX_FRAME_TITLE,
    },
    illinois.STATE_CODE: {
        "name": illinois.STATE_NAME,
        "calculate": illinois.calculate_illinois_tax,
        "field_labels": illinois.STATE_FIELD_LABELS,
        "estimate_label": illinois.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": illinois.STATE_TAX_FRAME_TITLE,
    },
    virginia.STATE_CODE: {
        "name": virginia.STATE_NAME,
        "calculate": virginia.calculate_virginia_tax,
        "field_labels": virginia.STATE_FIELD_LABELS,
        "estimate_label": virginia.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": virginia.STATE_TAX_FRAME_TITLE,
    },
    pennsylvania.STATE_CODE: {
        "name": pennsylvania.STATE_NAME,
        "calculate": pennsylvania.calculate_pennsylvania_tax,
        "field_labels": pennsylvania.STATE_FIELD_LABELS,
        "estimate_label": pennsylvania.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": pennsylvania.STATE_TAX_FRAME_TITLE,
    },
    north_carolina.STATE_CODE: {
        "name": north_carolina.STATE_NAME,
        "calculate": north_carolina.calculate_north_carolina_tax,
        "field_labels": north_carolina.STATE_FIELD_LABELS,
        "estimate_label": north_carolina.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": north_carolina.STATE_TAX_FRAME_TITLE,
    },
    new_york.STATE_CODE: {
        "name": new_york.STATE_NAME,
        "calculate": new_york.calculate_new_york_tax,
        "field_labels": new_york.STATE_FIELD_LABELS,
        "estimate_label": new_york.STATE_ESTIMATED_TAX_LABEL,
        "frame_title": new_york.STATE_TAX_FRAME_TITLE,
    },
}


def get_available_states() -> dict[str, str]:
    return {
        code: config["name"]
        for code, config in sorted(
            STATE_MODULES.items(),
            key=lambda item: item[1]["name"],
        )
    }


def get_state_config(state_code: str) -> dict:
    return STATE_MODULES[state_code]


def calculate_state_tax(state_code: str, state_inputs: dict, filing_status: str) -> dict:
    return STATE_MODULES[state_code]["calculate"](state_inputs, filing_status)


__all__ = [
    "STATE_MODULES",
    "calculate_state_tax",
    "get_available_states",
    "get_state_config",
]
