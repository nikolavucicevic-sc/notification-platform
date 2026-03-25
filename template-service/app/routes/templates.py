from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.template import Template
from app.schemas import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateRenderRequest,
    TemplateRenderResponse
)
from app.services.template_renderer import TemplateRenderer
import uuid

router = APIRouter()


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template"""

    # Validate template syntax
    is_valid, error_msg, extracted_vars = TemplateRenderer.validate_template(template.body)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    if template.channel_type.value == "EMAIL" and template.subject:
        is_valid_subject, error_msg_subject, subject_vars = TemplateRenderer.validate_template(template.subject)
        if not is_valid_subject:
            raise HTTPException(status_code=400, detail=f"Subject error: {error_msg_subject}")
        extracted_vars = list(set(extracted_vars + subject_vars))

    # Check if template name already exists
    existing = db.query(Template).filter(Template.name == template.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template with this name already exists")

    # Validate EMAIL template has subject
    if template.channel_type.value == "EMAIL" and not template.subject:
        raise HTTPException(status_code=400, detail="EMAIL templates must have a subject")

    # Create template
    db_template = Template(
        id=uuid.uuid4(),
        name=template.name,
        description=template.description,
        channel_type=template.channel_type,
        subject=template.subject,
        body=template.body,
        variables=",".join(extracted_vars) if extracted_vars else None
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    # Convert to response
    return template_to_response(db_template)


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    channel_type: str = None,
    db: Session = Depends(get_db)
):
    """List all templates"""
    query = db.query(Template)

    if channel_type:
        query = query.filter(Template.channel_type == channel_type)

    templates = query.order_by(Template.created_at.desc()).all()
    return [template_to_response(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get a specific template"""
    template = db.query(Template).filter(Template.id == uuid.UUID(template_id)).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template_to_response(template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update a template"""
    db_template = db.query(Template).filter(Template.id == uuid.UUID(template_id)).first()

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields
    update_data = template_update.model_dump(exclude_unset=True)

    # Validate body if updated
    if "body" in update_data:
        is_valid, error_msg, extracted_vars = TemplateRenderer.validate_template(update_data["body"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        update_data["variables"] = ",".join(extracted_vars) if extracted_vars else None

    # Validate subject if updated
    if "subject" in update_data and update_data["subject"]:
        is_valid, error_msg, subject_vars = TemplateRenderer.validate_template(update_data["subject"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Subject error: {error_msg}")

    for key, value in update_data.items():
        if key != "variables" or "body" not in update_data:  # Only update variables if body changed
            setattr(db_template, key, value)

    db.commit()
    db.refresh(db_template)

    return template_to_response(db_template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Delete a template"""
    db_template = db.query(Template).filter(Template.id == uuid.UUID(template_id)).first()

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(db_template)
    db.commit()


@router.post("/render", response_model=TemplateRenderResponse)
async def render_template(
    render_request: TemplateRenderRequest,
    db: Session = Depends(get_db)
):
    """Render a template with provided variables"""
    db_template = db.query(Template).filter(
        Template.id == uuid.UUID(render_request.template_id)
    ).first()

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Render body
    rendered_body, missing_body_vars = TemplateRenderer.render(
        db_template.body,
        render_request.variables
    )

    # Render subject if EMAIL
    rendered_subject = None
    missing_subject_vars = []
    if db_template.subject:
        rendered_subject, missing_subject_vars = TemplateRenderer.render(
            db_template.subject,
            render_request.variables
        )

    # Combine missing variables
    missing_vars = list(set(missing_body_vars + missing_subject_vars))

    # Get template variables
    template_vars = db_template.variables.split(",") if db_template.variables else []

    return TemplateRenderResponse(
        subject=rendered_subject,
        body=rendered_body,
        channel_type=db_template.channel_type,
        variables_used=template_vars,
        missing_variables=missing_vars
    )


def template_to_response(template: Template) -> TemplateResponse:
    """Convert Template model to TemplateResponse"""
    variables = template.variables.split(",") if template.variables else []
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description,
        channel_type=template.channel_type,
        subject=template.subject,
        body=template.body,
        variables=variables,
        created_at=template.created_at,
        updated_at=template.updated_at
    )
