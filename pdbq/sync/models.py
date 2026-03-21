from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrgRecord(BaseModel):
    id: int
    name: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class NetworkRecord(BaseModel):
    id: int
    org_id: Optional[int] = None
    asn: Optional[int] = None
    name: Optional[str] = None
    aka: Optional[str] = None
    website: Optional[str] = None
    info_type: Optional[str] = None
    info_prefixes4: Optional[int] = None
    info_prefixes6: Optional[int] = None
    policy_general: Optional[str] = None
    policy_locations: Optional[str] = None
    policy_ratio: Optional[bool] = None
    policy_contracts: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class IXRecord(BaseModel):
    id: int
    org_id: Optional[int] = None
    name: Optional[str] = None
    name_long: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region_continent: Optional[str] = None
    media: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class FacilityRecord(BaseModel):
    id: int
    org_id: Optional[int] = None
    name: Optional[str] = None
    aka: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    country: Optional[str] = None
    clli: Optional[str] = None
    rencode: Optional[str] = None
    npanxx: Optional[str] = None
    tech: Optional[str] = None
    sales_email: Optional[str] = None
    sales_phone: Optional[str] = None
    tech_email: Optional[str] = None
    tech_phone: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class IXLanRecord(BaseModel):
    id: int
    ix_id: Optional[int] = None
    name: Optional[str] = None
    descr: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class IXPfxRecord(BaseModel):
    id: int
    ixlan_id: Optional[int] = None
    prefix: Optional[str] = None
    protocol: Optional[str] = None
    in_dfz: Optional[bool] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class NetIXLanRecord(BaseModel):
    id: int
    net_id: Optional[int] = None
    ixlan_id: Optional[int] = None
    asn: Optional[int] = None
    ipaddr4: Optional[str] = None
    ipaddr6: Optional[str] = None
    speed: Optional[int] = None
    is_rs_peer: Optional[bool] = None
    operational: Optional[bool] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class NetFacRecord(BaseModel):
    id: int
    net_id: Optional[int] = None
    fac_id: Optional[int] = None
    local_asn: Optional[int] = None
    avail_sonet: Optional[bool] = None
    avail_ethernet: Optional[bool] = None
    avail_atm: Optional[bool] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class PoCRecord(BaseModel):
    id: int
    net_id: Optional[int] = None
    role: Optional[str] = None
    visible: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class CarrierRecord(BaseModel):
    id: int
    org_id: Optional[int] = None
    name: Optional[str] = None
    aka: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class CarrierFacRecord(BaseModel):
    id: int
    carrier_id: Optional[int] = None
    fac_id: Optional[int] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class CampusRecord(BaseModel):
    id: int
    org_id: Optional[int] = None
    name: Optional[str] = None
    aka: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
