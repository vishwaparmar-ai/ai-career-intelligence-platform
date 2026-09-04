import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export function Button({
  variant = "primary",
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "w-full rounded-full px-5 py-2.5 text-sm font-medium transition-colors disabled:opacity-50",
        variant === "primary" && "bg-navy text-paper hover:bg-navy-light",
        variant === "ghost" && "bg-transparent text-ink/70 hover:text-ink",
        className
      )}
      {...props}
    />
  );
}
