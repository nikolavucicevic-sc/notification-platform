import { useState, useEffect } from 'react';
import { templateApi } from '../services/api';
import { Template, TemplateCreate, ChannelType } from '../types/template';
import toast from 'react-hot-toast';
import './TemplateManager.css';

export function TemplateManager() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [filterChannel, setFilterChannel] = useState<string>('');

  const [formData, setFormData] = useState<TemplateCreate>({
    name: '',
    description: '',
    channel_type: ChannelType.EMAIL,
    subject: '',
    body: '',
  });

  useEffect(() => {
    loadTemplates();
  }, [filterChannel]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await templateApi.getTemplates(filterChannel || undefined);
      setTemplates(data);
    } catch (error) {
      toast.error('Failed to load templates');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      channel_type: ChannelType.EMAIL,
      subject: '',
      body: '',
    });
    setEditingTemplate(null);
    setShowForm(false);
  };

  const handleEdit = (template: Template) => {
    setFormData({
      name: template.name,
      description: template.description || '',
      channel_type: template.channel_type,
      subject: template.subject || '',
      body: template.body,
    });
    setEditingTemplate(template);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate EMAIL templates have subject
    if (formData.channel_type === ChannelType.EMAIL && !formData.subject) {
      toast.error('Email templates must have a subject');
      return;
    }

    try {
      if (editingTemplate) {
        await templateApi.updateTemplate(editingTemplate.id, formData);
        toast.success('Template updated successfully!');
      } else {
        await templateApi.createTemplate(formData);
        toast.success('Template created successfully!');
      }
      resetForm();
      loadTemplates();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to save template';
      toast.error(errorMsg);
      console.error(error);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete template "${name}"?`)) return;

    try {
      await templateApi.deleteTemplate(id);
      toast.success('Template deleted');
      loadTemplates();
    } catch (error) {
      toast.error('Failed to delete template');
      console.error(error);
    }
  };

  // Extract variables from text
  const extractVariables = (text: string): string[] => {
    const regex = /\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}/g;
    const matches = text.matchAll(regex);
    const vars = Array.from(matches, m => m[1]);
    return [...new Set(vars)]; // Return unique variables
  };

  const getTemplateVariables = () => {
    const bodyVars = extractVariables(formData.body);
    const subjectVars = formData.subject ? extractVariables(formData.subject) : [];
    return [...new Set([...bodyVars, ...subjectVars])];
  };

  return (
    <div className="template-manager">
      <div className="template-header">
        <h2>📝 Template Manager</h2>
        <div className="header-actions">
          <select
            value={filterChannel}
            onChange={(e) => setFilterChannel(e.target.value)}
            className="channel-filter"
          >
            <option value="">All Channels</option>
            <option value="EMAIL">Email</option>
            <option value="SMS">SMS</option>
          </select>
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            {showForm ? 'Cancel' : '+ Create Template'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="template-form">
          <h3>{editingTemplate ? 'Edit Template' : 'Create New Template'}</h3>

          <div className="form-row">
            <div className="form-group">
              <label>Template Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Welcome Email"
                required
              />
            </div>

            <div className="form-group">
              <label>Channel Type *</label>
              <select
                value={formData.channel_type}
                onChange={(e) => setFormData({ ...formData, channel_type: e.target.value as ChannelType })}
                required
              >
                <option value={ChannelType.EMAIL}>Email</option>
                <option value={ChannelType.SMS}>SMS</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Description</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of this template"
            />
          </div>

          {formData.channel_type === ChannelType.EMAIL && (
            <div className="form-group">
              <label>Subject *</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                placeholder="e.g., Welcome {{first_name}}!"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Body *</label>
            <textarea
              value={formData.body}
              onChange={(e) => setFormData({ ...formData, body: e.target.value })}
              placeholder="Hello {{first_name}},\n\nWelcome to our platform!\n\nUse {{variable_name}} for dynamic content."
              rows={8}
              required
            />
          </div>

          <div className="variables-preview">
            <strong>Variables detected:</strong>{' '}
            {getTemplateVariables().length > 0 ? (
              getTemplateVariables().map(v => (
                <span key={v} className="variable-badge">{`{{${v}}}`}</span>
              ))
            ) : (
              <span className="text-muted">No variables found</span>
            )}
          </div>

          <div className="form-actions">
            <button type="button" onClick={resetForm} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-submit">
              {editingTemplate ? 'Update Template' : 'Create Template'}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="loading">Loading templates...</div>
      ) : (
        <div className="template-list">
          {templates.length === 0 ? (
            <div className="empty-state">
              {filterChannel
                ? `No ${filterChannel} templates found`
                : 'No templates yet. Create one to get started!'}
            </div>
          ) : (
            templates.map(template => (
              <div key={template.id} className="template-card">
                <div className="template-card-header">
                  <div>
                    <h4>{template.name}</h4>
                    <span className={`channel-badge channel-${template.channel_type.toLowerCase()}`}>
                      {template.channel_type}
                    </span>
                  </div>
                  <div className="card-actions">
                    <button onClick={() => handleEdit(template)} className="btn-edit" title="Edit">
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(template.id, template.name)}
                      className="btn-delete"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                {template.description && (
                  <p className="template-description">{template.description}</p>
                )}

                {template.subject && (
                  <div className="template-field">
                    <strong>Subject:</strong> {template.subject}
                  </div>
                )}

                <div className="template-field">
                  <strong>Body:</strong>
                  <div className="template-body-preview">{template.body}</div>
                </div>

                <div className="template-meta">
                  <div className="variables-list">
                    <strong>Variables:</strong>{' '}
                    {template.variables.length > 0 ? (
                      template.variables.map(v => (
                        <span key={v} className="variable-badge">{`{{${v}}}`}</span>
                      ))
                    ) : (
                      <span className="text-muted">None</span>
                    )}
                  </div>
                  <div className="template-dates">
                    Created: {new Date(template.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
