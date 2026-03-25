export enum ChannelType {
  EMAIL = 'EMAIL',
  SMS = 'SMS',
}

export interface Template {
  id: string;
  name: string;
  description?: string;
  channel_type: ChannelType;
  subject?: string;
  body: string;
  variables: string[];
  created_at: string;
  updated_at: string;
}

export interface TemplateCreate {
  name: string;
  description?: string;
  channel_type: ChannelType;
  subject?: string;
  body: string;
  variables?: string[];
}

export interface TemplateUpdate {
  name?: string;
  description?: string;
  channel_type?: ChannelType;
  subject?: string;
  body?: string;
  variables?: string[];
}

export interface TemplateRenderRequest {
  template_id: string;
  variables: Record<string, any>;
}

export interface TemplateRenderResponse {
  subject?: string;
  body: string;
  channel_type: ChannelType;
  variables_used: string[];
  missing_variables: string[];
}
