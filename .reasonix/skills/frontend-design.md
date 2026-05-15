---
name: frontend-design
description: 前端组件/页面设计技能 — 从设计方案到组件树、状态管理、样式方案和 TDD 实现
---

# Frontend Design — 前端设计与实现

基于 obra/superpowers 方法论的前端实施技能。当你有经过批准的设计方案后，使用本技能将设计转化为前端代码。

**使用时机：** 在 `brainstorming`（需求澄清）和 `writing-plans`（编写计划）之后，进入具体前端实现时。

---

## 核心原则

- **设计先于代码** — 在写任何 HTML/CSS/JS 之前先确定组件结构
- **TDD 优先** — 先编写失败测试，再写最小实现代码
- **YAGNI** — 只实现当前需要的，不为"未来可能"的功能加代码
- **移动优先** — 从最小屏幕开始设计，然后适配大屏

---

## 第一阶段：组件架构设计

### 1.1 拆解设计稿

将设计方案的每个界面拆解为组件树：

```
页面
├── Header
│   ├── Logo
│   └── Navigation
│       └── NavItem
├── Sidebar
│   ├── FilterGroup
│   │   └── FilterItem
│   └── SearchBox
├── MainContent
│   └── CardGrid
│       └── Card
│           ├── CardImage
│           ├── CardTitle
│           └── CardActions
└── Footer
```

**每个组件要回答：**
- 它的职责是什么？
- 它的输入（props）是什么？
- 它的状态（state）是什么？
- 它依赖哪些其他组件？

### 1.2 定义数据流

- **状态类型**：服务端数据 / UI 状态 / 表单状态 / 路由状态
- **状态管理**：Context / 全局 store / 本地 state / URL params
- **数据获取**：加载态 / 空态 / 错误态 / 成功态

### 1.3 文件结构规划

```
src/
├── components/          # 通用组件
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── Button.module.css
│   └── Card/
│       ├── Card.tsx
│       ├── Card.test.tsx
│       └── Card.module.css
├── features/            # 功能模块
│   └── product-list/
│       ├── ProductListPage.tsx
│       ├── ProductListPage.test.tsx
│       ├── ProductCard.tsx
│       ├── ProductCard.test.tsx
│       └── useProducts.ts
├── hooks/               # 共享 hooks
├── services/            # API 调用
├── types/               # TypeScript 类型
└── utils/               # 工具函数
```

---

## 第二阶段：组件级设计

对每个组件，在设计文档或注释中确定：

### 2.1 Props 接口

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  label: string;
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}
```

### 2.2 状态与行为

```typescript
// 本地状态
const [expanded, setExpanded] = useState(false);
// 派生状态（不需要额外 state）
const hasItems = items.length > 0;
// 副作用
useEffect(() => { fetchData(); }, []);
```

### 2.3 样式方案

明确选择一种并保持一致：
- CSS Modules / Tailwind / styled-components / 原生 CSS
- 命名约定：BEM / utility classes
- 响应式断点

---

## 第三阶段：TDD 实现

对每个组件按以下步骤实施：

### 步骤 1：编写测试（RED）

```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with label', () => {
    render(<Button variant="primary" size="md" label="Submit" onClick={() => {}} />);
    expect(screen.getByText('Submit')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button variant="primary" size="md" label="Click" onClick={handleClick} />);
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when disabled prop is set', () => {
    render(<Button variant="primary" size="md" label="Submit" onClick={() => {}} disabled />);
    expect(screen.getByText('Submit')).toBeDisabled();
  });
});
```

### 步骤 2：确认测试失败

```bash
npm test Button.test.tsx -- --watch
# Expected: FAIL — component not yet implemented
```

### 步骤 3：编写最小实现（GREEN）

```typescript
// Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  label: string;
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export function Button({ variant, size, label, onClick, disabled, loading }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? '加载中...' : label}
    </button>
  );
}
```

### 步骤 4：确认测试通过

```bash
npm test Button.test.tsx -- --watch
# Expected: PASS
```

### 步骤 5：提交

```bash
git add .
git commit -m "feat: add Button component with primary/secondary/ghost variants"
```

---

## 设计决策检查表

在每个组件实现前，确认以下问题：

| 问题 | 选项 |
|------|------|
| 这个组件需要独立存在吗？ | 独立组件 / 合并到父组件 |
| 状态放在哪里？ | 本地 state / Context / store / URL |
| 如何处理加载态？ | 骨架屏 / spinner / 渐进式加载 |
| 如何处理错误？ | 错误边界 / toast / inline 提示 |
| 如何处理空态？ | 空状态插图 / 引导创建 |
| 需要无障碍支持吗？ | aria 属性 / 键盘导航 / 屏幕阅读器 |
| 需要动画吗？ | CSS transition / framer-motion / 无动画 |

---

## 红线（避免的反模式）

| 反模式 | 正确做法 |
|--------|----------|
| 在写好测试之前写组件代码 | 先写测试（RED → GREEN） |
| 一个组件做太多事 | 拆分为更小的组件 |
| props 层层透传超过 3 层 | 使用 Context 或组合 |
| 在组件内直接调用 API | 抽取到 service/hook |
| 没有测试边界情况 | 测试加载态、空态、错误态、极限值 |
| 样式全局污染 | 使用 CSS Modules / scoped styles |
