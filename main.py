import copy


def create_flow(service_specs: list, pod_specs: list, flow_uuid, seed_script, db_name, db_user, db_password):

    # Prepare the seed script
    init_script = f"""
#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
for i in {{1..30}}; do
    if pg_isready -h localhost -U $POSTGRES_USER; then
        break
    fi
    echo "Waiting for PostgreSQL to be ready..."
    sleep 1
done

if [ $i -eq 30 ]; then
    echo "Timeout waiting for PostgreSQL to be ready"
    exit 1
fi

cat << EOF > /tmp/init.sql
{seed_script}
EOF

# Execute the SQL script
PGPASSWORD=$POSTGRES_PASSWORD /usr/bin/psql -U $POSTGRES_USER -d $POSTGRES_DB -f /tmp/init.sql

# Check for errors
if [ $? -ne 0 ]; then
    echo "Error executing SQL script"
    exit 1
fi

echo "SQL script executed successfully"
"""

    modified_pod_specs = []

    for pod_spec in pod_specs:
        modified_pod_spec = copy.deepcopy(pod_spec)
        container = modified_pod_spec['containers'][0]

        # Add environment variables
        container['env'] = container.get('env', []) + [
            {'name': 'POSTGRES_DB', 'value': db_name},
            {'name': 'POSTGRES_USER', 'value': db_user},
            {'name': 'POSTGRES_PASSWORD', 'value': db_password},
        ]

        # Add PostStart lifecycle hook to the Postgres container
        lifecycle = {
            'postStart': {
                'exec': {
                    'command': ['/bin/bash', '-c', init_script]
                }
            }
        }
        container['lifecycle'] = lifecycle

        modified_pod_specs.append(modified_pod_spec)
    
    return {
        "pod_specs": modified_pod_specs,
        "config_map": {}
    }


def delete_flow(config_map, flow_uuid):
    pass
