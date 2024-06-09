import json

from marshmallow import Schema, fields, EXCLUDE, post_load, validates, ValidationError
from FlaredUI.Modules.DB.Models import User, OAuth, Tunnel, ContainerManagement, VMManagement, Server, Container, VM, \
    Application, ApiKeys, AppSettings, PluginRepository, Plugin


# --- Helper function to handle exposed ports in schemas ---
def format_exposed_ports(obj):
    if obj.exposed_ports:
        return [{'port': port, 'protocol': protocol}
                for protocol, ports in json.loads(obj.exposed_ports).items()
                for port in ports]
    return []


# --- Schemas ---
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class OAuthLoginSchema(Schema):
    provider = fields.Str(required=True)


class OAuthSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    provider_id = fields.Int(required=True)
    oauth_id = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


class TunnelSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    uuid = fields.Str(required=True)
    domain = fields.Str(required=True)
    description = fields.Str(required=True)
    tlds = fields.List(fields.String)


class ContainerManagementSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class VMManagementSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    exposed_ports = fields.Method(serialize=format_exposed_ports, deserialize='load_exposed_ports', allow_none=True)
    server_id = fields.Int(required=True)
    container_id = fields.Int(allow_none=True)
    vm_id = fields.Int(allow_none=True)
    hostname = fields.Str()
    enabled = fields.Bool(default=False)
    tunnel_id = fields.Int(allow_none=True)
    tunnels = fields.List(fields.Int())

    def load_exposed_ports(self, value):
        # Parse the exposed_ports data to match the database format
        if not value:
            return {}

        exposed_ports = {}
        for entry in value:
            protocol = entry.get('protocol')
            port = entry.get('port')
            if protocol and port:
                exposed_ports.setdefault(protocol, []).append(port)
        return exposed_ports


class ContainerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    image = fields.Str()
    state = fields.Str()
    server_id = fields.Int(required=True)
    hostname = fields.Str()
    enabled = fields.Bool(default=False)
    applications = fields.Nested('ApplicationSchema', many=True, exclude=('container',))


class VMSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    os_type = fields.Str(required=True)
    os_name = fields.Str(required=True)
    os_version = fields.Str(required=True)
    cpu_cores = fields.Int()
    memory = fields.Int()
    storage = fields.Int()
    state = fields.Str()
    guest_os_id = fields.Str()
    creation_time = fields.DateTime()
    server_id = fields.Int(required=True)
    enabled = fields.Bool(default=False)
    applications = fields.Nested('ApplicationSchema', many=True, exclude=('vm',))


class VMCreateSchema(Schema):
    name = fields.Str(required=True)
    os_type = fields.Str(required=True)
    os_name = fields.Str(required=True)
    os_version = fields.Str(required=True)
    cpu_cores = fields.Int(required=True)
    memory = fields.Int(required=True)
    storage = fields.Int(required=True)
    server_id = fields.Int(required=True)
    enabled = fields.Bool(default=False)


class ServerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    hostname = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    ssh_port = fields.Int(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)  # Password only during creation/update
    container_manager_id = fields.Int(required=True)
    vm_manager_id = fields.Int(required=True)
    namespace = fields.Str(allow_none=True)
    containers = fields.Nested('ContainerSchema', many=True, exclude=('server',))
    vms = fields.Nested('VMSchema', many=True, exclude=('server',))
    applications = fields.Nested('ApplicationSchema', many=True, exclude=('server',))


class ApiKeySchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Exclude unknown fields from input data

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    user_id = fields.Int(required=True)
    description = fields.Str(required=False)


class AppSettingsSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Exclude unknown fields from input data

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    value = fields.Str(required=True)
    last_modified = fields.DateTime(dump_only=True)
    modified_by = fields.Int(required=True)


class PluginRepositorySchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Exclude unknown fields from input data

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    added_at = fields.DateTime(dump_only=True)


class PluginSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Exclude unknown fields from input data

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    repository_id = fields.Int(required=True)
    version = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    entry_point = fields.Str(allow_none=True)
    requires = fields.List(fields.Str(), allow_none=True)
    installed = fields.Bool(default=False)
    active = fields.Bool(default=False)
    installed_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# --- OAuth Provider Model ---
class OAuthProviderSchema(Schema):
    id = fields.Int(dump_only=True)
    platform = fields.Str(required=True)
    client_id = fields.Str(required=True)
    client_secret = fields.Str(required=True)
    enabled = fields.Boolean(default=False)


# --- Cloudflare Routes Model --
class ApplicationTunnelSchema(Schema):
    """Schema for creating/updating a route (application-tunnel association)."""

    application_id = fields.Int(required=True)
    tunnel_id = fields.Int(required=True)

    @validates("application_id")
    def validate_application_id(self, value):
        application = Application.query.get(value)
        if not application:
            raise ValidationError(f"Application with ID {value} not found.")

    @validates("tunnel_id")
    def validate_tunnel_id(self, value):
        tunnel = Tunnel.query.get(value)
        if not tunnel:
            raise ValidationError(f"Tunnel with ID {value} not found.")
