from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.auth import get_current_tenant_id

router = APIRouter(prefix="/customers", tags=["customers"], redirect_slashes=False)


@router.post("/", response_model=CustomerResponse, status_code=201)
@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    ctx: tuple = Depends(get_current_tenant_id),
):
    tenant_id, _ = ctx
    db_customer = Customer(**customer.model_dump(), tenant_id=tenant_id)
    db.add(db_customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists for this tenant")
    db.refresh(db_customer)
    return db_customer


@router.get("/", response_model=list[CustomerResponse])
@router.get("", response_model=list[CustomerResponse])
def get_customers(
    db: Session = Depends(get_db),
    ctx: tuple = Depends(get_current_tenant_id),
):
    tenant_id, role = ctx
    if role == "SUPER_ADMIN":
        return db.query(Customer).all()
    return db.query(Customer).filter(Customer.tenant_id == tenant_id).all()


@router.get("/email/{email}", response_model=CustomerResponse)
def get_customer_by_email(
    email: str,
    db: Session = Depends(get_db),
    ctx: tuple = Depends(get_current_tenant_id),
):
    tenant_id, role = ctx
    q = db.query(Customer).filter(Customer.email == email)
    if role != "SUPER_ADMIN":
        q = q.filter(Customer.tenant_id == tenant_id)
    customer = q.first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    ctx: tuple = Depends(get_current_tenant_id),
):
    tenant_id, role = ctx
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if role != "SUPER_ADMIN" and str(customer.tenant_id) != tenant_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    ctx: tuple = Depends(get_current_tenant_id),
):
    tenant_id, role = ctx
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if role != "SUPER_ADMIN" and str(customer.tenant_id) != tenant_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    for field, value in customer_data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    ctx: tuple = Depends(get_current_tenant_id),
):
    tenant_id, role = ctx
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if role != "SUPER_ADMIN" and str(customer.tenant_id) != tenant_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
