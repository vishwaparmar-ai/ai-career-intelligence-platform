import { cn } from "@/lib/utils";

type FieldProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

export function Field({ label, error, className, id, ...props }: FieldProps) {
  const inputId = id ?? props.name;

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={inputId} className="text-sm font-medium text-ink">
        {label}
      </label>
      <input
        id={inputId}
        className={cn(
          "rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink placeholder:text-ink/40",
          "focus:border-navy",
          error && "border-gap",
          className
        )}
        {...props}
      />
      {error && <span className="text-xs text-gap">{error}</span>}
    </div>
  );
}
