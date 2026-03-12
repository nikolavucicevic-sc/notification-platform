# Notification Platform Frontend

A React + TypeScript frontend for the notification platform.

## Features

- Send email notifications with subject, body, and customer IDs
- View all sent notifications with status tracking
- Real-time status updates (PENDING, PROCESSING, COMPLETED, FAILED)
- Responsive design with modern UI

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will run on http://localhost:3000

## Backend Integration

The frontend is configured to proxy API requests to the backend running on http://localhost:8000.

Make sure the notification-service backend is running before starting the frontend.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Technology Stack

- React 18
- TypeScript
- Vite
- Axios for API calls
