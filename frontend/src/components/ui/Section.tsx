interface SectionProps {
  label?: string;
  children?: React.ReactNode;
  className?: string;
}

export default function Section(props: SectionProps) {
  return (
    <div className="px-6 flex flex-col gap-5 flex-1">
      <p className="text-h2/[24px] text-white">{props.label}</p>
      {props.children && (
        <div className={`flex gap-4 justify-center ${props.className}`}>
          {props.children}
        </div>
      )}
    </div>
  );
}
