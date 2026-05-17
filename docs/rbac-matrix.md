# RBAC Matrix

## System Roles

| system_role | Register | Login | Manage Users | Resolve Disputes | View Audit Logs |
|---|:---:|:---:|:---:|:---:|:---:|
| user | — | ✓ | — | — | — |
| moderator | — | ✓ | — | ✓ | ✓ |
| admin | — | ✓ | ✓ | — | ✓ |

## Contextual Roles (defined by order participation)

| Action | client | freelancer | moderator | admin |
|---|:---:|:---:|:---:|:---:|
| Create task | ✓ | ✓ | — | — |
| Edit task (before order) | ✓ (own) | — | — | — |
| Create offer | — | ✓ | — | — |
| Accept offer | ✓ (own task) | — | — | — |
| Confirm order | ✓ | ✓ | — | — |
| Read chat | ✓ (own order) | ✓ (own order) | — | — |
| Send message | ✓ (own order) | ✓ (own order) | — | — |
| Upload file | — | ✓ (own order) | — | — |
| Download file | ✓ (own order) | ✓ (own order) | — | — |
| Submit work | — | ✓ (own order) | — | — |
| Complete order | ✓ (own order) | — | — | — |
| Open dispute | ✓ (own order) | ✓ (own order) | — | — |
| Resolve dispute | — | — | ✓ | — |
| Deposit escrow | ✓ | ✓ | — | — |

## Key Rule

`client` and `freelancer` are NOT separate account types.
They are contextual roles determined by the user's participation in a specific task/order.
One `user` can be `client` in one order and `freelancer` in another simultaneously.
