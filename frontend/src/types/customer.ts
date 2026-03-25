export interface Customer {
  id: string;
  email: string;
  phone_number?: string;
  first_name?: string;
  last_name?: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerCreate {
  email: string;
  phone_number?: string;
  first_name?: string;
  last_name?: string;
}
