# code-quality/SKILL.md

## Clean Separation of Concerns

### Frontend (React + TypeScript + Tailwind)
- Components only: UI rendering, state management via React Query/Hooks
- No API logic, no business logic, no data transformation
- Type safety: all props typed, no `any` unless explicitly justified
- Component directory: `components/{feature}/{Component}.tsx`
- Hooks: custom hooks in `hooks/` directory, reusable logic extracted
- CSS: Tailwind utility-first, custom components in `components/ui/` (shadcn/ui)
- No inline styles except for experimental features with justification

### Backend (FastAPI + Python)
- API routes only: request validation, response serialization
- No frontend code, no chart libraries, no UI components
- Pydantic models for all request/response schemas
- Dependency injection for DB, auth, external services
- Environment-based configuration

### Analytics
- Data transformation/calculations only
- No API routes, no component rendering
- Reusable calculation functions, pure functions preferred
- Testable in isolation without HTTP server

### Integrations
- Monday.com API client: authentication, rate limiting, webhook handling
- Error handling and retries specific to external service
- No business logic, pure integration concerns
- Mockable for testing

### Shared/Utils
- Shared types/interfaces that cross-cutting concerns use
- Date formatting utilities
- String helpers
- Formatting functions (currency, percent, file size)

### Import Rules
- Frontend never imports from backend, except shared types explicitly marked
- Backend never imports from frontend
- Analytics can import from both frontend types and backend models, but minimally
- Utils import from other utils only, no circular dependencies

### TypeScript Guidelines
- Strict mode enabled noImplicitAny, strictNullChecks
- Interfaces for public APIs, types for internal
- Shared types in `types/` directory, versioned
- Enum pattern: string enums for API values, const enums for internal

### Python Guidelines
- Type hints on all public functions
- Docstrings on all modules, classes, public functions
- Black formatting, isort imports, flake8 linting
- Async where I/O bound, sync where CPU bound
- Pydantic v2 for models with strict mode