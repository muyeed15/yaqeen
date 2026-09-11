import { ReactNode } from "react";
import { BackButton } from "./BackButton";

type Props = {
  title?: string;
  subtitle?: string;
  showBack?: boolean;
  /** Logical parent route for the back button. */
  backHref?: string;
  children?: ReactNode;
};

export function PageHeader({ title, subtitle, showBack, backHref, children }: Props) {
  return (
    <div className="bg-white px-4 h-16 flex items-center gap-3 border-b border-sage/80">
      {showBack && <BackButton href={backHref} />}
      {children ? (
        children
      ) : (
        <div>
          <p className="text-[10px] text-navy-muted font-semibold uppercase tracking-widest leading-none">
            {subtitle || "\u00A0"}
          </p>
          <h1 className="text-navy font-bold text-lg leading-tight mt-0.5">{title}</h1>
        </div>
      )}
    </div>
  );
}
