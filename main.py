import copy

def create_flow(service_spec, deployment_spec, flow_uuid, seed_script, db_name, db_user, db_password):
    modified_deployment_spec = copy.deepcopy(deployment_spec)
    container = modified_deployment_spec['template']['spec']['containers'][0]
    container['env'] = container.get('env', []) + [
        {'name': 'POSTGRES_DB', 'value': db_name},
        {'name': 'POSTGRES_USER', 'value': db_user},
        {'name': 'POSTGRES_PASSWORD', 'value': db_password},
    ]
    
    # Prepare the seed script
    escaped_script = seed_script.replace("'", "'\\''")
    init_script = f"""
cat << EOF > /tmp/init.sql
{escaped_script}
EOF
psql -U $POSTGRES_USER -d $POSTGRES_DB -f /tmp/init.sql
"""
    
    init_container = {
        'name': 'postgres-init',
        'image': 'postgres:latest',
        'command': ['bash', '-c', init_script],
        'env': container['env']
    }
    modified_deployment_spec['template']['spec']['initContainers'] = [init_container]
    return {
        "deployment_spec": modified_deployment_spec,
        "config_map": {}
    }

def delete_flow(config_map, flow_uuid):
    pass
