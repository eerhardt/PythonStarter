# React + Vite Application

This is a React application built with Vite, providing a minimal setup with HMR (Hot Module Replacement) and ESLint rules.

## Prerequisites

- Node.js (version 18 or higher)
- npm (comes with Node.js)

## Getting Started

### Install Dependencies

Before running the application for the first time, install the required dependencies:

```bash
cd react-vite-app
npm install
```

### Run Development Server

To start the development server with hot module replacement:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` by default.

### Build for Production

To create an optimized production build:

```bash
npm run build
```

The built files will be generated in the `dist/` directory.

### Preview Production Build

To preview the production build locally:

```bash
npm run preview
```

### Lint Code

To run ESLint and check for code quality issues:

```bash
npm run lint
```

## Project Structure

- `src/` - Application source code
  - `App.jsx` - Main application component
  - `main.jsx` - Application entry point
- `public/` - Static assets
- `index.html` - HTML entry point
- `vite.config.js` - Vite configuration

## Learn More

- [Vite Documentation](https://vite.dev/)
- [React Documentation](https://react.dev/)
