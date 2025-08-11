from apps.api.models import Organization

def get_or_create_org(db, org_name: str):
    org = db.query(Organization).filter(Organization.name == org_name).first()
    if not org:
        org = Organization(name=org_name, zendesk_subdomain=None)
        db.add(org); db.commit(); db.refresh(org)
    return org
