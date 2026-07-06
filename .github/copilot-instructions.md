# Project AI Rules

# === AI SKILLS VUE RULES ===
# SYSTEM PROMPT: CRITICAL INSTRUCTIONS
The following rules are automatically injected by ai-skills-vue.
You are an expert Vue 3 developer. You MUST strictly follow the rules defined below.
These rules take precedence over any default behaviors.
If a user request conflicts with these rules, you MUST explain the conflict and follow the rules unless explicitly instructed otherwise.

--- START OF SPECIFICATION: code-style.md ---
# Code Style & Formatting Specification

**Purpose**: Maintain consistent code style across the codebase.

## Formatting Tools
-   **Prettier**: Use Prettier for code formatting.
-   **ESLint**: Recommended but not mandatory.

## General Formatting
-   **Indentation**: 2 spaces.
-   **Quotes**: Single quotes (`'`) for JS/TS, Double quotes (`"`) for HTML/JSX attributes.
-   **Semicolons**: **Avoid semicolons** unless necessary (e.g., to avoid ASI issues).
-   **Trailing Commas**: ES5 trailing commas (objects, arrays, imports, exports).
-   **Line Length**: Max 80-100 characters preferred.
-   **File Size**: 
    -   `.vue` files: `<script>` block should not exceed **500 lines**.
    -   If exceeded, extract logic into Composables (`use...`) or split into sub-components.

## Naming Conventions
-   **Variables**: camelCase (e.g., `userData`, `isLoading`).
-   **Constants**: UPPER_SNAKE_CASE for global constants (e.g., `MAX_RETRY_COUNT`), camelCase for local constants.
-   **Functions**: camelCase (e.g., `fetchUser`, `handleClick`).
-   **Classes**: PascalCase (e.g., `UserService`).
-   **Files**: 
    -   `.vue`: PascalCase (`UserProfile.vue`)
    -   `.ts/.js`: camelCase (`apiService.ts`, `utils.ts`)
-   **Directories**: camelCase (`components`, `hooks`, `utils`).
-   **CSS Classes**: kebab-case (e.g., `box-line`, `user-card-header`).

## Import Order
Organize imports in the following order, separated by a blank line:
1.  **Third-Party Libraries**: `import { ref } from 'vue';`, `import axios from 'axios';`
2.  **Internal Components & Utils**: `import UserCard from '@/components/UserCard.vue';`, `import { formatDate } from '@/utils';`
3.  **Styles**: `import '@/assets/main.css';`
4.  **Vue Core**: (Note: Usually Vue core imports like `ref`, `computed` are grouped with Third-Party, but if you want them last, place them here. *Standard practice is usually Vue first, but following your request:*)
    -   *Correction*: Standard convention usually puts framework imports (Vue) at the very top. If you strictly want "Third Party -> Internal -> Styles -> Vue Core", please confirm. 
    -   **Recommended Order**:
        1.  **Vue Core & Ecosystem**: `vue`, `vue-router`, `pinia`.
        2.  **Third-Party Libs**: `axios`, `lodash`, `dayjs`.
        3.  **Internal Aliases**: `@/components`, `@/utils`, `@/api`.
        4.  **Relative Imports**: `./components`, `../utils`.
        5.  **Styles**: `./style.css`.

## CSS / Tailwind
-   **Class Naming**: kebab-case (e.g., `main-container`, `submit-btn`).
-   **Scoped Styles**: Always use `<style scoped>` in Vue components.
-   **Tailwind**: Prefer utility classes over custom CSS.

## TypeScript
-   **Types**: Use `interface` for object shapes, `type` for unions/intersections.
-   **Explicit Types**: Avoid `any`. Use explicit types or generics whenever possible.
-   **Enums**: Use `const enum` or union types instead of standard `enum`.

## Example
```typescript
// Imports
import { ref, computed } from 'vue'; // Vue Core
import axios from 'axios'; // Third-Party
import UserCard from '@/components/UserCard.vue'; // Internal
import '@/assets/styles/main.css'; // Styles

// Logic
const MAX_ITEMS = 10;

// No semicolons
const count = ref(0)

interface User {
  id: number
  name: string
}
```

--- END OF SPECIFICATION: code-style.md ---

--- START OF SPECIFICATION: comment-standards.md ---
# Comment Specification

**Purpose**: Ensure code is readable, maintainable, and self-documenting.

## General Rules
-   **Language**: Comments should be in **Chinese** (unless project specifies otherwise).
-   **Placement**: Comments must be placed **above** the code they describe, not at the end of the line.
-   **Clarity**: Explain *why*, not *what*. The code shows *what* is happening; comments should explain the intent or complex logic.
-   **Outdated Comments**: Delete comments that no longer match the code.
-   **Comment Ratio**: Ensure a minimum comment density of **12%** in `.vue`, `.ts`, and `.js` files.
    -   This includes JSDoc, inline explanations, and section headers.
    -   Do not add trivial comments just to meet the quota (e.g., `// increment i` for `i++`). Focus on business logic and "why".

## File Headers
Every file (`.vue`, `.ts`, `.js`, `.css`, etc.) MUST start with a standard header comment block containing Author, Date, and Description.

**Format:**
```
/*
 * @Author: [Author Name]
 * @Date: [YYYY-MM-DD HH:mm:ss]
 * @Description: [Brief description of the file's purpose]
 */
```

**Vue Template Example:**
```html
<!--
 * @Author: zhangxiaofeng
 * @Date: 2026-01-29 10:35:31
 * @Description: 我的对话页面 - 从 AI_Native 转换而来
-->
```

## Vue Template Comments
-   **Section Dividers**: Use HTML comments to separate major logical sections in the template.
    -   Example: `<!-- Section: User Info -->`, `<!-- Section: Action Buttons -->`
-   **Conditional Logic**: Explain complex `v-if` conditions with a comment above the element.

## JSDoc / TSDoc
-   **Functions/Methods**: Use JSDoc for all public functions, exported utilities, and complex logic.
    -   `@param`: Describe parameters.
    -   `@returns`: Describe return value.
    -   `@example`: Provide a usage example if helpful.
-   **Components**: Add a top-level comment describing the component's purpose.
-   **Props/Types**: Comment on complex prop definitions or interface properties.

## Inline Comments
-   **Complex Logic**: Add a single-line comment (`//`) above complex blocks of code.
-   **TODOs**: Use `// TODO: [Description]` for pending tasks.
-   **FIXMEs**: Use `// FIXME: [Description]` for known bugs or hacks.

## Example
```typescript
/*
 * @Author: DevTeam
 * @Date: 2026-03-02 10:00:00
 * @Description: 日期处理工具函数
 */

/**
 * 将日期字符串格式化为用户的本地格式。
 * 
 * @param date - 要格式化的日期字符串或 Date 对象
 * @param locale - 语言环境代码（例如 'zh-CN'）
 * @returns 格式化后的日期字符串
 */
export function formatDate(date: string | Date, locale: string = 'zh-CN'): string {
  // 如果日期无效，直接返回空字符串
  if (!date) return '';
  
  return new Intl.DateTimeFormat(locale).format(new Date(date));
}
```

--- END OF SPECIFICATION: comment-standards.md ---

--- START OF SPECIFICATION: component-standards.md ---
# Component Specification

**Purpose**: Define how Vue components should be structured and written.

## Component Structure
-   **Single File Components (SFC)**: Always use `.vue` files.
-   **Script Setup**: Always use `<script setup lang="ts">`.
-   **Style**: Use `<style scoped lang="less">` (unless project specifies Tailwind-only).
-   **Order**:
    1.  `<template>`
    2.  `<script setup>`
    3.  `<style scoped>`

## Naming Conventions
-   **File Names**: PascalCase (e.g., `UserProfile.vue`, `OrderList.vue`).
-   **Component Names**: Multi-word PascalCase (e.g., `UserCard`, not `Card`).
-   **Complex Components**: For complex components, use a directory structure:
    -   `components/UserCard/index.vue`
    -   `components/UserCard/types.ts`
    -   `components/UserCard/utils.ts`
-   **Props**: camelCase in script, kebab-case in template.
-   **Events**: camelCase in script (e.g., `emit('updateValue')`), kebab-case in template (`@update-value`).

## Logic Organization
-   **Props Definition**: Use `defineProps<Props>()` with a TypeScript interface.
    -   **Destructuring**: Prefer destructuring props directly (Vue 3.3+): `const { title, isActive = false } = defineProps<Props>();`
    -   Do not use array syntax for props.
-   **v-model**: Use `defineModel` (Vue 3.4+) for two-way binding.
    -   Example: `const model = defineModel<string>()`
    -   Avoid manual `props` + `emit('update:modelValue')` boilerplate.
-   **Emits Definition**: Use `defineEmits<{ (e: 'event', value: type): void }>()`.
-   **Reusability**: Extract complex logic into Composables (`use...` hooks).

## Template Rules
-   **Directives**: Use shorthands (`:` for `v-bind`, `@` for `v-on`, `#` for `v-slot`).
-   **Self-closing tags**: Use self-closing tags for components without content (e.g., `<MyComponent />`).
-   **Conditionals**: Prefer `v-if` over `v-show` unless toggling frequency is high.
-   **Loops**: Always provide a unique `:key` when using `v-for`.

## Example
```vue
<template>
  <div class="p-4 border rounded" @click="emit('click', '123')">
    <h2 :class="titleClass">{{ title }}</h2>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  title: string;
  isActive?: boolean;
}

// Vue 3.3+ Destructuring with default values
const { title, isActive = false } = defineProps<Props>();

const emit = defineEmits<{
  (e: 'click', id: string): void;
}>();

const titleClass = computed(() => isActive ? 'text-blue-500' : 'text-gray-500');
</script>

<style scoped lang="less">
.border {
  border: 1px solid #ddd;
}
</style>
```

--- END OF SPECIFICATION: component-standards.md ---

--- START OF SPECIFICATION: core-libraries.md ---
# Core Library Specification

**Purpose**: Define the primary technology stack and libraries to be used in the project.

## Technology Stack
-   **Framework**: Vue 3 (Composition API)
-   **Build Tool**: Vite
-   **Language**: TypeScript (Strict Mode)
-   **Package Manager**: pnpm (preferred) or npm

## UI & Styling
-   **UI Library**: Ant Design Vue (`ant-design-vue`)
    -   Use standard AntD components for all UI elements.
    -   Do not introduce other UI libraries (e.g., Element Plus, Vuetify) unless explicitly requested.
-   **CSS Framework**: Tailwind CSS
    -   Use Tailwind utility classes for layout, spacing, and custom styling.
    -   Avoid writing raw CSS/SCSS unless absolutely necessary for complex animations or overrides.
-   **Icons**: `@ant-design/icons-vue` or `lucide-vue-next`

## Essential Libraries
-   **Routing**: Vue Router (`vue-router`)
-   **State Management**: Pinia (`pinia`)
-   **HTTP Client**: Axios (`axios`) or a wrapper based on it.
-   **Date Handling**: Day.js (`dayjs`)
-   **Utility Library**: Lodash-es (`lodash-es`) or VueUse (`@vueuse/core`)

## Constraints
-   **Do NOT** use Options API.
-   **Do NOT** use jQuery or direct DOM manipulation.
-   **Do NOT** use `moment.js` (use Day.js instead).

--- END OF SPECIFICATION: core-libraries.md ---

--- START OF SPECIFICATION: directory-structure.md ---
# Project Directory Specification

**Purpose**: Define a standard directory structure for consistency and scalability.

## Root Structure
```
/
├── public/             # Static assets served as-is (favicon, robots.txt)
├── src/                # Source code
│   ├── api/            # API definition files (grouped by domain)
│   ├── assets/         # Static assets (images, global css)
│   ├── components/     # Shared/Global UI components
│   ├── composables/    # Shared Vue Composables (hooks)
│   ├── layout/         # Layout components (Sidebar, Header, AppLayout)
│   ├── modules/        # [LARGE SCALE] Feature modules (DDD/Modular)
│   ├── router/         # Vue Router configuration
│   ├── stores/         # Pinia stores
│   ├── types/          # Global TypeScript type definitions
│   ├── utils/          # Shared utility functions
│   ├── views/          # Page components (routed views)
│   ├── App.vue         # Root component
│   └── main.ts         # Application entry point
├── tests/              # Test files (if not co-located)
├── .env                # Shared environment variables
├── .env.development    # Development-specific variables
├── .env.production     # Production-specific variables
├── index.html          # Entry HTML
├── package.json        # Dependencies and scripts
├── tsconfig.json       # TypeScript config
└── vite.config.ts      # Vite config
```

## Detailed Rules
-   **`views/`**: Structure by feature/route.
    -   Example: `views/user/UserList.vue`, `views/user/UserProfile.vue`.
-   **`components/`**:
    -   `components/common/`: Generic, app-wide components (e.g., `BaseButton`, `LoadingSpinner`).
    -   `components/business/`: Domain-specific components used in multiple views.
-   **`assets/`**:
    -   `assets/images/`: Image files.
    -   `assets/styles/`: Global CSS/SCSS files (e.g., `main.css`, `variables.css`).
-   **`utils/`**:
    -   **`tools.ts`**: Encapsulate general algorithms and reusable logic here.
    -   Other utility files can be created for specific domains (e.g., `request.ts`, `date.ts`), but generic helpers go in `tools.ts`.

## Modular Structure (For Large Features)
For complex, large-scale features (e.g., "Order Management", "User Dashboard"), use a **Modular/DDD (Domain-Driven Design)** structure under `src/modules/`. This keeps related logic co-located.

**Structure:**
```
src/modules/
├── order-management/       # Feature Module Name
│   ├── api/                # Module-specific API calls
│   ├── components/         # Module-specific components (private)
│   ├── composables/        # Module-specific hooks
│   ├── stores/             # Module-specific Pinia stores
│   ├── types/              # Module-specific types
│   ├── views/              # Module-specific pages/routes
│   ├── router.ts           # Module route definitions (export to main router)
│   └── index.ts            # Public API (exports for other modules)
```

**Guidelines:**
-   **Co-location**: Keep everything related to the feature inside the module folder.
-   **Encapsulation**: Components inside `modules/order-management/components` are private to this module. If they need to be shared, move them to `src/components/`.
-   **Lazy Loading**: The main router should lazy-load the module's routes.

## File Naming
-   **Directories**: camelCase (e.g., `userProfile`).
-   **Vue Files**: PascalCase (e.g., `UserProfile.vue`).
-   **TS/JS Files**: camelCase (e.g., `userApi.ts`).

--- END OF SPECIFICATION: directory-structure.md ---

--- START OF SPECIFICATION: error-handling.md ---
# Error Handling & Monitoring Specification

**Purpose**: Standardize error management and monitoring for large-scale applications.

## Global Error Handling
-   **Vue Error Handler**:
    -   Use `app.config.errorHandler` to catch unhandled errors in components.
    -   Log errors to console and monitoring service (e.g., Sentry).
-   **Promise Rejection**:
    -   Use `window.addEventListener('unhandledrejection', ...)` to catch unhandled promise rejections.
-   **Error Boundaries**:
    -   Use `onErrorCaptured` hook in layout or high-level components to catch errors from descendants and prevent app crashes.

## API Error Handling
-   **Centralized Handling**:
    -   Use Axios interceptors to handle standard HTTP errors (401, 403, 404, 500).
    -   Map backend error codes to user-friendly messages.
-   **Retry Logic**:
    -   Implement automatic retries for transient network errors (e.g., 503, timeout) with exponential backoff.
-   **User Feedback**:
    -   Show global toast/notification for critical errors.
    -   Show inline error messages for form validation or specific component errors.

## Monitoring & Logging
-   **Sentry Integration**:
    -   Initialize Sentry in `main.ts`.
    -   Capture exceptions with context (user ID, environment, release version).
-   **Performance Monitoring**:
    -   Track API response times and critical user interactions.
-   **Log Levels**:
    -   Use appropriate log levels (`debug`, `info`, `warn`, `error`).
    -   Disable `debug` and `info` logs in production builds.

## Example (Global Error Handler)
```typescript
// main.ts
import { createApp } from 'vue';
import App from './App.vue';
import * as Sentry from '@sentry/vue';

const app = createApp(App);

app.config.errorHandler = (err, instance, info) => {
  console.error('Global Error:', err);
  Sentry.captureException(err, {
    extra: { component: instance?.$options.name, info }
  });
};

app.mount('#app');
```

--- END OF SPECIFICATION: error-handling.md ---

--- START OF SPECIFICATION: git-workflow.md ---
# Git Workflow & Collaboration Specification

**Purpose**: Standardize version control and team collaboration processes.

## Branching Strategy
-   **Model**: Trunk Based Development (Recommended for CI/CD) or Git Flow.
-   **Main Branches**:
    -   `main` (or `master`): Production-ready code. Protected branch.
    -   `develop`: Integration branch for features.
-   **Feature Branches**:
    -   Format: `feat/description` or `fix/issue-id-description`.
    -   Example: `feat/user-login`, `fix/jira-123-cart-error`.

## Commit Convention
Follow **Conventional Commits** specification:
`type(scope): description`

-   **Types**:
    -   `feat`: New feature.
    -   `fix`: Bug fix.
    -   `docs`: Documentation changes.
    -   `style`: Formatting, missing semi colons, etc; no code change.
    -   `refactor`: Refactoring production code.
    -   `test`: Adding tests, refactoring test; no production code change.
    -   `chore`: Updating build tasks, package manager configs, etc; no production code change.
-   **Example**: `feat(auth): implement login with google`

## Code Review (MR/PR)
-   **Size**: Keep PRs small (< 400 lines of code changes).
-   **Checklist**:
    -   [ ] Tests passed (Unit & Component).
    -   [ ] Linting passed (ESLint & Prettier).
    -   [ ] No console.logs or debuggers.
    -   [ ] Complex logic is commented.
-   **Approval**: Require at least 1 approval from a senior developer before merging.

## CI/CD Integration
-   **Pre-commit Hooks**: Use `husky` + `lint-staged` to run linting and type checking on staged files.
-   **Commit Message Linting**: Use `commitlint` to enforce commit message format.

--- END OF SPECIFICATION: git-workflow.md ---

--- START OF SPECIFICATION: http-requests.md ---
# HTTP Request Specification

**Purpose**: Standardize API interaction and data fetching.

## Library
-   **Axios**: Use Axios for HTTP requests.
-   **Wrapper**: Create a centralized `request.ts` or `http.ts` instance with interceptors.

## Architecture
-   **Location**: `src/api/`
-   **Structure**: Group API calls by domain (e.g., `src/api/user.ts`, `src/api/order.ts`).
-   **Service Layer**: Components should call API functions, not `axios.get()` directly.
-   **Naming Conventions**: Follow RESTful naming patterns:
    -   `get[Resource]`: GET requests (e.g., `getUser`, `getOrderList`).
    -   `create[Resource]`: POST requests (e.g., `createUser`).
    -   `update[Resource]`: PUT/PATCH requests (e.g., `updateUser`).
    -   `delete[Resource]`: DELETE requests (e.g., `deleteUser`).

## Request/Response Standards
-   **Interceptors**:
    -   **Request**: Attach auth tokens (e.g., Bearer token from Pinia/localStorage).
    -   **Response**: Handle global errors (401 Unauthorized, 403 Forbidden, 500 Server Error) centrally.
    -   **Data Unwrapping**: Return `response.data` directly if the backend wraps data in a standard envelope (e.g., `{ code: 200, data: ... }`).
-   **Types**: Define TypeScript interfaces for Request Parameters and Response Data for every API call.
-   **Cancellation**: Support `AbortController` to cancel pending requests when components unmount or when race conditions occur.
    -   Pass an optional `signal` parameter to API functions.

## Hook Integration
-   **VueUse**: Consider using `useAsyncState` or custom hooks (`useRequest`) to manage loading/error states in components.
-   **Auto-Cancellation**: Encapsulate `AbortController` logic within hooks to automatically cancel requests on unmount.

## Advanced Communication Patterns

### Server-Sent Events (SSE)
-   **Usage**: Use for one-way server-to-client streaming (e.g., AI responses, notifications).
-   **Implementation**:
    -   Use `fetch` with `ReadableStream` (via `fetch-event-source` or native) if headers/POST are needed.
    -   Use native `EventSource` for simple GET requests.
-   **Reconnection**: Implement auto-reconnect logic with exponential backoff.
-   **Typing**: Define interfaces for event payloads.

### WebSocket
-   **Usage**: Use for real-time, bi-directional communication (e.g., chat, collaborative editing).
-   **Management**: Singleton instance managed via a Pinia store or a dedicated service class.
-   **Heartbeat**: Implement ping/pong mechanism to detect dead connections.
-   **Reconnection**: Auto-reconnect on disconnect.
-   **State**: Expose connection status (`CONNECTING`, `OPEN`, `CLOSED`) to the UI.

### File Upload
-   **Method**: Use `FormData` for file uploads.
-   **Progress**: Expose upload progress via `onUploadProgress` (Axios).
-   **Structure**:
    ```typescript
    export function uploadFile(file: File, onProgress?: (percent: number) => void) {
      const formData = new FormData();
      formData.append('file', file);
      return request.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(percent);
          }
        }
      });
    }
    ```

## Example

**1. API Definition (`src/api/user.ts`)**
```typescript
import request from '@/utils/request';
import type { User, LoginParams } from '@/types/user';

export function login(data: LoginParams) {
  return request.post<{ token: string }>('/auth/login', data);
}

export function getUserProfile() {
  return request.get<User>('/user/profile');
}
```

**2. Component Usage**
```vue
<script setup lang="ts">
import { ref } from 'vue';
import { getUserProfile } from '@/api/user';

const user = ref();

async function loadData() {
  try {
    user.value = await getUserProfile();
  } catch (error) {
    console.error('Failed to load user', error);
  }
}
</script>
```

--- END OF SPECIFICATION: http-requests.md ---

--- START OF SPECIFICATION: performance-optimization.md ---
# Performance Optimization Specification

**Purpose**: Ensure high performance and responsiveness for large-scale applications.

## Loading Performance
-   **Route Lazy Loading**: All routes **MUST** use dynamic imports.
    ```typescript
    // router/index.ts
    const UserProfile = () => import('@/views/user/UserProfile.vue');
    ```
-   **Component Lazy Loading**: Use `defineAsyncComponent` for heavy components (e.g., charts, maps, rich text editors) that are not immediately visible.
-   **Image Optimization**:
    -   Use modern formats (WebP/AVIF).
    -   Implement lazy loading for images below the fold (`loading="lazy"`).
    -   Use CDN for all static assets.

## Runtime Performance
-   **Virtual Scrolling**: For lists with **>100 items**, use virtual scrolling (e.g., `vue-virtual-scroller` or AntD `VirtualList`).
    -   **Do NOT** render large lists directly in the DOM.
-   **Reactivity Optimization**:
    -   Use `shallowRef` for large immutable data structures (e.g., charts config, map data) to avoid deep reactivity overhead.
    -   Avoid unnecessary `watch` with `deep: true`.
-   **Event Handling**:
    -   Debounce high-frequency events (input, resize, scroll) using `lodash-es/debounce`.
    -   Clean up event listeners and timers in `onUnmounted`.

## Bundle Optimization
-   **Tree Shaking**: Ensure all libraries support ES Modules. Import only what is needed (e.g., `import { Button } from 'ant-design-vue';`).
-   **Chunk Splitting**: Configure Vite `build.rollupOptions.output.manualChunks` to split vendor code:
    ```typescript
    // vite.config.ts
    manualChunks(id) {
      if (id.includes('node_modules')) {
        if (id.includes('echarts')) return 'echarts';
        if (id.includes('ant-design-vue')) return 'antd';
        return 'vendor';
      }
    }
    ```

## Metrics & Monitoring
-   **Core Web Vitals**: Monitor LCP (Largest Contentful Paint), FID (First Input Delay), and CLS (Cumulative Layout Shift).
-   **Performance Budget**: Set limits on bundle size (e.g., initial JS < 200KB).

--- END OF SPECIFICATION: performance-optimization.md ---

--- START OF SPECIFICATION: security-standards.md ---
# Security Standards Specification

**Purpose**: Define security best practices to protect the application and user data.

## Data Security
-   **Sensitive Data**:
    -   **Do NOT** store sensitive data (passwords, PII, payment info) in `localStorage` or `sessionStorage` in plain text.
    -   Use `httpOnly` cookies for authentication tokens whenever possible.
    -   If using tokens in storage, ensure they have short expiration times and refresh mechanisms.
-   **Input Sanitization**:
    -   **Do NOT** use `v-html` unless absolutely necessary.
    -   If `v-html` is required, **MUST** sanitize content using `DOMPurify` before rendering.
    -   Validate all user inputs on both client and server sides.

## Network Security
-   **CSRF Protection**:
    -   Ensure API requests include CSRF tokens if using cookie-based authentication.
    -   Configure `SameSite` cookie attributes correctly (`Strict` or `Lax`).
-   **XSS Prevention**:
    -   Enable Content Security Policy (CSP) headers on the server.
    -   Avoid inline scripts and styles.
-   **HTTPS**:
    -   Force HTTPS for all communications.

## Dependency Management
-   **Auditing**:
    -   Run `npm audit` regularly to identify vulnerabilities.
    -   Update dependencies to patched versions immediately.
-   **Lockfile**:
    -   Commit `package-lock.json` to ensure consistent dependency versions.

## API Security
-   **Error Handling**:
    -   **Do NOT** expose stack traces or sensitive server details in API error responses displayed to the user.
-   **Rate Limiting**:
    -   Handle `429 Too Many Requests` gracefully with exponential backoff.

--- END OF SPECIFICATION: security-standards.md ---

--- START OF SPECIFICATION: state-management.md ---
# State Management Specification

**Purpose**: Define how to manage application state using Pinia.

## Library
-   **Pinia**: The exclusive state management library. Do not use Vuex.

## Store Structure
-   **Location**: `src/stores/`
-   **Naming**: `use[StoreName]Store.ts` (e.g., `useUserStore.ts`, `useCartStore.ts`).
-   **Syntax**: Use **Setup Stores** (function syntax), not Option Stores.

## Rules
1.  **Global vs. Local**: Only put state in Pinia if it is shared across multiple unrelated components. Local component state should remain in `ref`/`reactive`.
2.  **Direct Access**: Access state and actions directly from the store instance.
3.  **Destructuring**: Use `storeToRefs` when destructuring state/getters to maintain reactivity. Actions can be destructured directly.
4.  **Type Safety**: Explicitly type complex state using interfaces (e.g., `ref<User | null>(null)`).
5.  **Interaction**: Stores can import and use other stores directly. Avoid circular dependencies.

## Advanced Features
-   **Persistence**: Use `pinia-plugin-persistedstate`.
    -   **Best Practice**: Explicitly specify `paths` to persist only necessary data (e.g., user tokens, preferences).
    -   **Storage**: Use `localStorage` by default; use `sessionStorage` for sensitive session data.
-   **Resetting State**: Since Setup Stores lack a built-in `$reset()` method, implement a `reset()` action pattern:
    -   Define a default state function.
    -   Expose a `reset` function that resets state to default values.

## Example
```typescript
// src/stores/useUserStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types/user';

export const useUserStore = defineStore('user', () => {
  // Default State Function
  const defaultState = (): User | null => null;

  // State
  const user = ref<User | null>(defaultState());
  
  // Getters
  const isLoggedIn = computed(() => !!user.value);
  
  // Actions
  function setUser(newUser: User) {
    user.value = newUser;
  }

  function reset() {
    user.value = defaultState();
  }

  return { user, isLoggedIn, setUser, reset };
}, {
  persist: {
    paths: ['user'], // Only persist user state
    storage: localStorage,
  }
});
```

```vue
// Usage in component
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/useUserStore';

const userStore = useUserStore();
const { user, isLoggedIn } = storeToRefs(userStore); // State needs storeToRefs
const { setUser, reset } = userStore; // Actions don't
</script>
```

--- END OF SPECIFICATION: state-management.md ---

--- START OF SPECIFICATION: testing-standards.md ---
# Automated Testing Specification

**Purpose**: Ensure code reliability and prevent regressions.

## Tools
-   **Unit Testing**: Vitest (`vitest`)
-   **Component Testing**: Vue Test Utils (`@vue/test-utils`)
-   **E2E Testing**: Cypress (`cypress`) or Playwright (`playwright`)
-   **Environment**: `jsdom` (preferred) or `happy-dom`

## Testing Strategy
1.  **Unit Tests**:
    -   **Scope**: Utils, Stores, Composables.
    -   **Mocking**: **MUST** mock all external API calls using `vi.mock` or `msw`. Do not make real network requests.
    -   **Pinia**: Use `setActivePinia` and `createPinia` to isolate store state between tests.
2.  **Component Tests**:
    -   **Behavior Driven**: Test user interactions (clicks, inputs) and expected DOM updates.
    -   **Snapshots**: Use sparingly for stable UI components to avoid brittle tests.
3.  **Coverage**: Aim for **>80%** statement coverage for core logic (`utils`, `stores`).

## Best Practices
-   **Selectors**: Use `data-testid` attributes (e.g., `data-testid="submit-btn"`) for selecting elements, rather than relying on CSS classes or tag names which may change.
-   **Async Handling**: Vue updates are asynchronous. Always `await` user interactions (`trigger`) and use `nextTick()` when asserting DOM changes.
-   **Parameterized Tests**: Use `it.each` for testing utility functions with multiple input/output scenarios.
-   **Isolation**: Ensure tests are independent. Use `beforeEach`/`afterEach` to clean up state or mocks.

## Example (Unit Test with Parameters)
```typescript
// utils/math.spec.ts
import { describe, it, expect } from 'vitest';
import { add } from './math';

describe('math utils', () => {
  it.each([
    [1, 2, 3],
    [-1, 1, 0],
    [0, 0, 0]
  ])('add(%i, %i) should return %i', (a, b, expected) => {
    expect(add(a, b)).toBe(expected);
  });
});
```

## Example (Component Test)
```typescript
// components/BaseButton.spec.ts
import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import BaseButton from './BaseButton.vue';

describe('BaseButton', () => {
  it('emits click event', async () => {
    const wrapper = mount(BaseButton);
    
    // Use data-testid for selection
    await wrapper.find('[data-testid="btn"]').trigger('click');
    
    // Assert event emission
    expect(wrapper.emitted('click')).toBeTruthy();
  });
});
```

## Example (Pinia Store Test)
```typescript
// stores/counter.spec.ts
import { setActivePinia, createPinia } from 'pinia';
import { describe, it, expect, beforeEach } from 'vitest';
import { useCounterStore } from './counter';

describe('Counter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('increments', () => {
    const counter = useCounterStore();
    expect(counter.count).toBe(0);
    counter.increment();
    expect(counter.count).toBe(1);
  });
});
```

--- END OF SPECIFICATION: testing-standards.md ---
