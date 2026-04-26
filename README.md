# schemadiff

> Compare database schema snapshots across environments and output human-readable migration diffs.

---

## Installation

```bash
pip install schemadiff
```

Or install from source:

```bash
git clone https://github.com/yourname/schemadiff.git
cd schemadiff && pip install -e .
```

---

## Usage

Capture schema snapshots from two environments, then run a diff:

```bash
# Export schema snapshots
schemadiff snapshot --url postgresql://user:pass@staging/db --output staging.json
schemadiff snapshot --url postgresql://user:pass@prod/db --output prod.json

# Compare snapshots and print migration diff
schemadiff diff staging.json prod.json
```

**Example output:**

```
[+] Table added: user_sessions
[-] Column removed: orders.legacy_id (integer)
[~] Column modified: products.price — type changed: integer → numeric(10,2)
[~] Index added: idx_users_email on users(email)
```

You can also use schemadiff directly in Python:

```python
from schemadiff import compare

diff = compare("staging.json", "prod.json")
for change in diff.changes:
    print(change.description)
```

---

## Supported Databases

- PostgreSQL
- MySQL / MariaDB
- SQLite

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

This project is licensed under the [MIT License](LICENSE).