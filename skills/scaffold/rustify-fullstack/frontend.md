## 前端初始化

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install -D @tailwindcss/vite tailwindcss
```

## vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:{PORT}',
    },
  },
})
```

## 依赖参考

```json
{
  "dependencies": {
    "lucide-react": "^1.11.0",
    "react": "^19",
    "react-dom": "^19"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4",
    "@vitejs/plugin-react": "^6",
    "tailwindcss": "^4",
    "typescript": "~6",
    "vite": "^8"
  }
}
```

## 说明

- 前端开发时用 `cd frontend && npm run dev`，vite 自动代理 `/api` 到后端
- 生产构建由 `build.rs` 自动触发，产物在 `frontend/dist/`
- 图标库使用 lucide-react，不使用 emoji
