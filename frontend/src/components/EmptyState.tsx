/**
 * 首页空状态组件
 * 展示产品入口信息和可点击的示例问数问题
 */
import { LineChart, Search, ShoppingBag, Sparkles } from "lucide-react";

type EmptyStateProps = {
  examples: string[];
  onUseExample: (example: string) => void;
};

const highlights = [
  { label: "混合检索", icon: Search },
  { label: "SQL 闭环", icon: LineChart },
  { label: "电商数仓", icon: ShoppingBag },
];

export function EmptyState({ examples, onUseExample }: EmptyStateProps) {
  return (
    <div className="mx-auto flex min-h-full max-w-5xl flex-col justify-center px-4 py-12">
      <div className="mb-10 max-w-3xl">
        <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-brand/25 bg-brand/10 px-3 py-1.5 text-sm font-semibold text-brand">
          <Sparkles className="h-4 w-4" aria-hidden="true" />
          Ecommerce Insight Agent
        </div>
        <h1 className="text-balance text-4xl font-semibold leading-tight text-slate sm:text-6xl">
          电商智能<span className="text-brand">问数</span>平台
        </h1>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {highlights.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="rounded-2xl border border-accent/10 bg-white/80 px-4 py-4 shadow-line transition hover:-translate-y-0.5 hover:border-accent/25 hover:shadow-panel">
              <Icon className="mb-5 h-5 w-5 text-accent" aria-hidden="true" />
              <div className="text-sm font-semibold text-slate">{item.label}</div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-2">
        {examples.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => onUseExample(example)}
            className="min-h-20 rounded-2xl border border-brand/10 bg-gradient-to-br from-white to-orange-50/70 px-4 py-4 text-left text-[15px] leading-6 text-slate transition hover:-translate-y-0.5 hover:border-brand/40 hover:bg-white hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-brand/35"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
