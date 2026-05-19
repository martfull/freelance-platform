from app.common.enums import ContractStatus
from app.core.exceptions import AppError

ALLOWED_TRANSITIONS: dict[ContractStatus, list[ContractStatus]] = {
    ContractStatus.PENDING_CONFIRMATION: [ContractStatus.ACTIVE, ContractStatus.CANCELLED],
    ContractStatus.ACTIVE: [ContractStatus.SUBMITTED, ContractStatus.DISPUTED, ContractStatus.CANCELLED],
    ContractStatus.SUBMITTED: [ContractStatus.COMPLETED, ContractStatus.DISPUTED],
    ContractStatus.DISPUTED: [ContractStatus.COMPLETED, ContractStatus.CANCELLED],
    ContractStatus.COMPLETED: [],
    ContractStatus.CANCELLED: [],
}


def transition(contract, new_status: ContractStatus) -> None:
    allowed = ALLOWED_TRANSITIONS.get(contract.status, [])
    if new_status not in allowed:
        raise AppError(
            f"Cannot transition contract from '{contract.status}' to '{new_status}'",
            {"current": contract.status, "requested": new_status},
        )
    contract.status = new_status
