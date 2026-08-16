from forge_core.contracts.models import ExternalAction


APPROVAL_REQUIRED_ACTIONS = frozenset({"publish_content", "send_message", "spend_money", "delete_data", "change_permissions"})


def requires_approval(action: ExternalAction) -> bool:
    """Unknown external actions default to requiring approval."""
    return action.action_type in APPROVAL_REQUIRED_ACTIONS or action.action_type.startswith("external_")
