# React Frontend - Modern UI Layer

**OVERVIEW**: React 19 + Vite frontend with hooks, routing, and API integration for patent analysis.

## STRUCTURE
```
front_end/src/
├── components/          # Reusable UI components
├── pages/              # Route-level page components
├── api/                # API client modules
├── hooks/              # Custom React hooks
└── utils/              # Utility functions
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| API client | `api/axios.js` | Centralized HTTP client |
| Patent components | `components/Patent*` | Search, details views |
| Routing | `App.jsx` | React Router setup |
| State management | Custom hooks | useState/useContext patterns |

## CONVENTIONS
- **Modern React**: Functional components with hooks only
- **Styling**: Tailwind CSS + framer-motion animations  
- **API calls**: Centralized axios client with error handling
- **Routing**: React Router v7 with lazy loading
- **Build**: Vite with React plugin

## ANTI-PATTERNS
- No class components - use functional hooks
- No direct DOM manipulation - React refs only
- No inline styles - use Tailwind classes
- No prop drilling - use context for global state