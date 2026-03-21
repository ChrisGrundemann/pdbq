-- PeeringDB DuckDB Schema
-- All tables include a raw_json TEXT column for forward compatibility.
-- status = 'ok' is the standard filter for active records.

CREATE TABLE IF NOT EXISTS sync_meta (
    resource TEXT PRIMARY KEY,
    last_synced_at TIMESTAMP,
    record_count INTEGER
);

-- Organizations
CREATE TABLE IF NOT EXISTS org (
    id INTEGER PRIMARY KEY,
    name TEXT,
    website TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);

-- Networks
CREATE TABLE IF NOT EXISTS network (
    id INTEGER PRIMARY KEY,
    org_id INTEGER,
    asn INTEGER,
    name TEXT,
    aka TEXT,
    website TEXT,
    info_type TEXT,
    info_prefixes4 INTEGER,
    info_prefixes6 INTEGER,
    policy_general TEXT,
    policy_locations TEXT,
    policy_ratio BOOLEAN,
    policy_contracts TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_network_asn ON network(asn);
CREATE INDEX IF NOT EXISTS idx_network_org_id ON network(org_id);
CREATE INDEX IF NOT EXISTS idx_network_status ON network(status);

-- Internet Exchanges
CREATE TABLE IF NOT EXISTS ix (
    id INTEGER PRIMARY KEY,
    org_id INTEGER,
    name TEXT,
    name_long TEXT,
    country TEXT,
    city TEXT,
    region_continent TEXT,
    media TEXT,
    notes TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_ix_org_id ON ix(org_id);
CREATE INDEX IF NOT EXISTS idx_ix_country ON ix(country);
CREATE INDEX IF NOT EXISTS idx_ix_region_continent ON ix(region_continent);
CREATE INDEX IF NOT EXISTS idx_ix_status ON ix(status);

-- Facilities
CREATE TABLE IF NOT EXISTS facility (
    id INTEGER PRIMARY KEY,
    org_id INTEGER,
    name TEXT,
    aka TEXT,
    website TEXT,
    city TEXT,
    state TEXT,
    zipcode TEXT,
    country TEXT,
    clli TEXT,
    rencode TEXT,
    npanxx TEXT,
    tech TEXT,
    sales_email TEXT,
    sales_phone TEXT,
    tech_email TEXT,
    tech_phone TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_facility_org_id ON facility(org_id);
CREATE INDEX IF NOT EXISTS idx_facility_country ON facility(country);
CREATE INDEX IF NOT EXISTS idx_facility_status ON facility(status);

-- IX LANs (sub-networks of an IX)
CREATE TABLE IF NOT EXISTS ixlan (
    id INTEGER PRIMARY KEY,
    ix_id INTEGER,
    name TEXT,
    descr TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_ixlan_ix_id ON ixlan(ix_id);
CREATE INDEX IF NOT EXISTS idx_ixlan_status ON ixlan(status);

-- IX LAN Prefixes
CREATE TABLE IF NOT EXISTS ixpfx (
    id INTEGER PRIMARY KEY,
    ixlan_id INTEGER,
    prefix TEXT,
    protocol TEXT,
    in_dfz BOOLEAN,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_ixpfx_ixlan_id ON ixpfx(ixlan_id);
CREATE INDEX IF NOT EXISTS idx_ixpfx_status ON ixpfx(status);

-- Network <-> IX LAN relationships (peering sessions)
CREATE TABLE IF NOT EXISTS netixlan (
    id INTEGER PRIMARY KEY,
    net_id INTEGER,
    ixlan_id INTEGER,
    asn INTEGER,
    ipaddr4 TEXT,
    ipaddr6 TEXT,
    speed INTEGER,
    is_rs_peer BOOLEAN,
    operational BOOLEAN,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_netixlan_net_id ON netixlan(net_id);
CREATE INDEX IF NOT EXISTS idx_netixlan_ixlan_id ON netixlan(ixlan_id);
CREATE INDEX IF NOT EXISTS idx_netixlan_asn ON netixlan(asn);
CREATE INDEX IF NOT EXISTS idx_netixlan_status ON netixlan(status);

-- Network <-> Facility relationships
CREATE TABLE IF NOT EXISTS netfac (
    id INTEGER PRIMARY KEY,
    net_id INTEGER,
    fac_id INTEGER,
    local_asn INTEGER,
    avail_sonet BOOLEAN,
    avail_ethernet BOOLEAN,
    avail_atm BOOLEAN,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_netfac_net_id ON netfac(net_id);
CREATE INDEX IF NOT EXISTS idx_netfac_fac_id ON netfac(fac_id);
CREATE INDEX IF NOT EXISTS idx_netfac_status ON netfac(status);

-- Points of Contact
CREATE TABLE IF NOT EXISTS poc (
    id INTEGER PRIMARY KEY,
    net_id INTEGER,
    role TEXT,
    visible TEXT,
    name TEXT,
    phone TEXT,
    email TEXT,
    url TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_poc_net_id ON poc(net_id);
CREATE INDEX IF NOT EXISTS idx_poc_status ON poc(status);

-- Carriers
CREATE TABLE IF NOT EXISTS carrier (
    id INTEGER PRIMARY KEY,
    org_id INTEGER,
    name TEXT,
    aka TEXT,
    website TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_carrier_org_id ON carrier(org_id);
CREATE INDEX IF NOT EXISTS idx_carrier_status ON carrier(status);

-- Carrier <-> Facility relationships
CREATE TABLE IF NOT EXISTS carrierfac (
    id INTEGER PRIMARY KEY,
    carrier_id INTEGER,
    fac_id INTEGER,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_carrierfac_carrier_id ON carrierfac(carrier_id);
CREATE INDEX IF NOT EXISTS idx_carrierfac_fac_id ON carrierfac(fac_id);
CREATE INDEX IF NOT EXISTS idx_carrierfac_status ON carrierfac(status);

-- Campuses
CREATE TABLE IF NOT EXISTS campus (
    id INTEGER PRIMARY KEY,
    org_id INTEGER,
    name TEXT,
    aka TEXT,
    website TEXT,
    status TEXT,
    created TIMESTAMP,
    updated TIMESTAMP,
    raw_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_campus_org_id ON campus(org_id);
CREATE INDEX IF NOT EXISTS idx_campus_status ON campus(status);
