#!/bin/bash
set -euo pipefail

: "${MYSQL_ROOT_PASSWORD:?MYSQL_ROOT_PASSWORD is required}"
: "${MYSQL_APP_USER:?MYSQL_APP_USER is required}"
: "${MYSQL_APP_PASSWORD:?MYSQL_APP_PASSWORD is required}"
: "${MYSQL_READONLY_USER:?MYSQL_READONLY_USER is required}"
: "${MYSQL_READONLY_PASSWORD:?MYSQL_READONLY_PASSWORD is required}"

validate_account_name() {
    local value="$1"
    local variable_name="$2"

    if [[ ! "$value" =~ ^[A-Za-z0-9_]+$ ]]; then
        echo "$variable_name must contain only letters, digits, and underscores" >&2
        exit 1
    fi
}

escape_sql_string() {
    # MySQL string literals escape backslashes with \\ and quotes with ''.
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e "s/'/''/g"
}

validate_account_name "$MYSQL_APP_USER" "MYSQL_APP_USER"
validate_account_name "$MYSQL_READONLY_USER" "MYSQL_READONLY_USER"

app_password="$(escape_sql_string "$MYSQL_APP_PASSWORD")"
readonly_password="$(escape_sql_string "$MYSQL_READONLY_PASSWORD")"

mysql --protocol=socket -uroot -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
    CREATE USER IF NOT EXISTS '${MYSQL_APP_USER}'@'%' IDENTIFIED BY '${app_password}';
    CREATE USER IF NOT EXISTS '${MYSQL_READONLY_USER}'@'%' IDENTIFIED BY '${readonly_password}';
    GRANT ALL PRIVILEGES ON meta.* TO '${MYSQL_APP_USER}'@'%';
    GRANT SELECT, SHOW VIEW ON dw.* TO '${MYSQL_READONLY_USER}'@'%';
    FLUSH PRIVILEGES;
EOSQL
